import datetime
import os
import logging
from datetime import datetime, date, timedelta
from typing import Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

logger = logging.getLogger(__name__)
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.instrument.instrument import Instrument
from algo.domain.timeframe import Timeframe


import upstox_client
from upstox_client.rest import ApiException

from algo.infrastructure.access_token import AccessToken
from algo.infrastructure.upstox.upstox_instrument_service import UpstoxInstrumentService
from algo.domain.instrument.broker_instrument import BrokerInstrument

def parse_timeframe(timeframe: Timeframe) -> Tuple[str, str]:
        tf = timeframe.value if hasattr(timeframe, 'value') else str(timeframe)
        if tf.endswith('min'):
            return (tf.replace('min', ''), 'minutes')
        if tf.endswith('m'):
            return (tf.replace('m', ''), 'minutes')
        if tf.endswith('h'):
            return (str(int(tf.replace('h', '')) * 60), 'minutes')
        if tf.endswith('d'):
            return (tf.replace('d', ''), 'days')
        if tf.endswith('w'):
            return (tf.replace('w', ''), 'weeks')
        if tf.isdigit():
            return (tf, 'minutes')
        raise ValueError(f"Invalid timeframe format: {tf}")

class UpstoxHistoricalDataRepository(HistoricalDataRepository):
    
    def _get_max_days_for_timeframe(self, timeframe: Timeframe) -> int:
        """Get maximum allowed days for a given timeframe based on Upstox API limits."""
        tf = timeframe.value if hasattr(timeframe, 'value') else str(timeframe)
        
        # For 1-60 minute intervals: 28 days
        if tf.endswith('min') or tf.endswith('m') or tf.isdigit():
            interval_value = int(tf.replace('min', '').replace('m', '') if not tf.isdigit() else tf)
            if 1 <= interval_value <= 60:
                return 28
        
        # For hour intervals (converted to minutes): 28 days  
        if tf.endswith('h'):
            hour_value = int(tf.replace('h', ''))
            if hour_value * 60 <= 60:  # Up to 1 hour (60 minutes)
                return 28
        
        # For 1-day interval: 9 years (approximately 3287 days)
        if tf.endswith('d'):
            day_value = int(tf.replace('d', ''))
            if day_value == 1:
                return 3287  # 9 years * 365.25 days
        
        # For 1-week interval: no limit (return a very large number)
        if tf.endswith('w'):
            return 999999
        
        # Default to 28 days for safety
        return 28
    
    def _split_date_range(self, start_date: date, end_date: date, max_days: int) -> List[Tuple[date, date]]:
        """Split a date range into smaller segments based on the maximum allowed days."""
        if max_days >= 999999:  # No limit
            return [(start_date, end_date)]
        
        segments = []
        current_start = start_date
        
        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=max_days - 1), end_date)
            segments.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
        
        return segments

    def _fetch_historical_data_segment(self, broker_instrument: BrokerInstrument, start_date: date, end_date: date, timeframe: Timeframe) -> List[dict]:
        """Fetch historical data for a single date segment."""
        thread_id = threading.current_thread().name
        segment_start_time = time.perf_counter()
        
        date_str_from = start_date.strftime("%Y-%m-%d")
        date_str_to = end_date.strftime("%Y-%m-%d")
        interval, unit = parse_timeframe(timeframe)
        
        logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: Creating API instance...")
        api_instance_start = time.perf_counter()
        api_instance = self.api_instance()
        api_instance_elapsed = time.perf_counter() - api_instance_start
        logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: API instance created in {api_instance_elapsed:.3f}s")
        
        logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: Calling Upstox API...")
        api_call_start = time.perf_counter()
        response = api_instance.get_historical_candle_data1(
            instrument_key=broker_instrument.instrument_key,
            interval=interval,
            unit=unit,
            from_date=date_str_from,
            to_date=date_str_to
        )
        api_call_elapsed = time.perf_counter() - api_call_start
        logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: Upstox API call completed in {api_call_elapsed:.3f}s")
        
        candles = response.data.candles if hasattr(response.data, 'candles') else []
        if not candles:
            logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: No candles returned")
            return []
        
        logger.debug(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: Processing {len(candles)} candles...")
        processing_start = time.perf_counter()
        data = [
            {
                "timestamp": datetime.fromisoformat(candle[0]),
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
                "oi": candle[6] if len(candle) > 6 else None
            }
            for candle in reversed(candles)
        ]
        processing_elapsed = time.perf_counter() - processing_start
        
        total_elapsed = time.perf_counter() - segment_start_time
        logger.info(f"[{thread_id}] Segment {date_str_from} to {date_str_to}: Completed in {total_elapsed:.3f}s "
                    f"(api_instance: {api_instance_elapsed:.3f}s, api_call: {api_call_elapsed:.3f}s, "
                    f"processing: {processing_elapsed:.3f}s, candles: {len(candles)})")
        return data
    
    def _fetch_segment_with_metadata(self, args: Tuple[BrokerInstrument, date, date, Timeframe]) -> Tuple[date, List[dict]]:
        """Wrapper for _fetch_historical_data_segment that returns metadata for sorting."""
        broker_instrument, start_date, end_date, timeframe = args
        data = self._fetch_historical_data_segment(broker_instrument, start_date, end_date, timeframe)
        return (start_date, data)

    def _fetch_segment_with_retry(self, args: Tuple[BrokerInstrument, date, date, Timeframe], max_retries: int = 3) -> Tuple[date, List[dict]]:
        """Fetch segment data with retry logic for failed attempts."""
        broker_instrument, start_date, end_date, timeframe = args
        last_exception = None
        thread_id = threading.current_thread().name
        retry_start_time = time.perf_counter()
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"[{thread_id}] Segment {start_date} to {end_date}: Attempt {attempt + 1}/{max_retries}")
                data = self._fetch_historical_data_segment(broker_instrument, start_date, end_date, timeframe)
                total_retry_time = time.perf_counter() - retry_start_time
                if attempt > 0:
                    logger.info(f"[{thread_id}] Segment {start_date} to {end_date}: Succeeded on attempt {attempt + 1} after {total_retry_time:.3f}s total")
                return (start_date, data)
            except Exception as exc:
                last_exception = exc
                logger.warning(f"[{thread_id}] Segment {start_date} to {end_date}: Attempt {attempt + 1} failed with error: {exc}")
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    # Exponential backoff: wait 1s, 2s, 4s between retries
                    wait_time = 2 ** attempt
                    logger.debug(f"[{thread_id}] Segment {start_date} to {end_date}: Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
        
        # If we reach here, all retries failed
        total_retry_time = time.perf_counter() - retry_start_time
        logger.error(f"[{thread_id}] Segment {start_date} to {end_date}: All {max_retries} attempts failed after {total_retry_time:.3f}s")
        raise RuntimeError(f"Failed to fetch segment {start_date} to {end_date} after {max_retries} attempts. Last error: {last_exception}")
    
    
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> HistoricalData:
        overall_start_time = time.perf_counter()
        logger.info(f"get_historical_data: Starting for instrument={instrument.instrument_key}, "
                    f"start_date={start_date}, end_date={end_date}, timeframe={timeframe}")
        
        try:
            # Get broker instrument from service
            logger.debug("get_historical_data: Getting broker instrument...")
            broker_service_start = time.perf_counter()
            broker_service = UpstoxInstrumentService()
            broker_instrument = broker_service.get_broker_instrument(instrument)
            broker_service_elapsed = time.perf_counter() - broker_service_start
            logger.info(f"get_historical_data: Broker instrument lookup completed in {broker_service_elapsed:.3f}s")
            
            if not broker_instrument:
                raise ValueError(f"No broker instrument mapping found for {instrument.instrument_key}")
            
            logger.debug(f"get_historical_data: Broker instrument found: {broker_instrument.instrument_key}")
            
            # Calculate the maximum allowed days for this timeframe
            max_days = self._get_max_days_for_timeframe(timeframe)
            
            # Check if we need to split the date range
            total_days = (end_date - start_date).days + 1
            logger.info(f"get_historical_data: Total days={total_days}, max_days_per_request={max_days}")
            
            if total_days <= max_days:
                # Single API call is sufficient
                logger.info("get_historical_data: Using single API call (no splitting needed)")
                fetch_start = time.perf_counter()
                data = self._fetch_historical_data_segment(broker_instrument, start_date, end_date, timeframe)
                fetch_elapsed = time.perf_counter() - fetch_start
                
                overall_elapsed = time.perf_counter() - overall_start_time
                logger.info(f"get_historical_data: Completed in {overall_elapsed:.3f}s "
                           f"(broker_lookup: {broker_service_elapsed:.3f}s, fetch: {fetch_elapsed:.3f}s, "
                           f"records: {len(data)})")
                return HistoricalData(data)
            else:
                # Split into multiple segments and make parallel API calls
                logger.debug("get_historical_data: Splitting date range into segments...")
                split_start = time.perf_counter()
                segments = self._split_date_range(start_date, end_date, max_days)
                split_elapsed = time.perf_counter() - split_start
                logger.info(f"get_historical_data: Date range split into {len(segments)} segments in {split_elapsed:.3f}s")
                
                for i, (seg_start, seg_end) in enumerate(segments):
                    logger.debug(f"get_historical_data: Segment {i+1}: {seg_start} to {seg_end}")
                
                # Prepare arguments for parallel execution
                segment_args = [(broker_instrument, segment_start, segment_end, timeframe) 
                               for segment_start, segment_end in segments]
                
                # Execute API calls in parallel with retry logic
                all_segment_data = []
                failed_segments = []
                
                num_workers = min(len(segments), 5)
                logger.info(f"get_historical_data: Starting parallel execution with {num_workers} workers for {len(segments)} segments")
                
                parallel_start = time.perf_counter()
                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    # Submit all tasks
                    submit_start = time.perf_counter()
                    future_to_segment = {
                        executor.submit(self._fetch_segment_with_retry, args): args 
                        for args in segment_args
                    }
                    submit_elapsed = time.perf_counter() - submit_start
                    logger.debug(f"get_historical_data: All {len(segments)} tasks submitted in {submit_elapsed:.3f}s")
                    
                    # Collect results as they complete
                    results_start = time.perf_counter()
                    completed_count = 0
                    for future in as_completed(future_to_segment):
                        args = future_to_segment[future]
                        segment_start, segment_end = args[1], args[2]
                        
                        try:
                            start_date_segment, segment_data = future.result()
                            all_segment_data.append((start_date_segment, segment_data))
                            completed_count += 1
                            logger.debug(f"get_historical_data: Segment {segment_start} to {segment_end} completed "
                                        f"({completed_count}/{len(segments)})")
                        except Exception as exc:
                            failed_segments.append({
                                'start_date': segment_start,
                                'end_date': segment_end,
                                'error': str(exc)
                            })
                            logger.error(f"get_historical_data: Segment {segment_start} to {segment_end} failed: {exc}")
                    
                    results_elapsed = time.perf_counter() - results_start
                    logger.debug(f"get_historical_data: All results collected in {results_elapsed:.3f}s")
                
                parallel_elapsed = time.perf_counter() - parallel_start
                logger.info(f"get_historical_data: Parallel execution completed in {parallel_elapsed:.3f}s "
                           f"(submit: {submit_elapsed:.3f}s, collect: {results_elapsed:.3f}s)")
                
                # Check if any segments failed
                if failed_segments:
                    error_details = "; ".join([
                        f"Segment {seg['start_date']} to {seg['end_date']}: {seg['error']}" 
                        for seg in failed_segments
                    ])
                    raise RuntimeError(f"Failed to fetch {len(failed_segments)} out of {len(segments)} segments. Details: {error_details}")
                
                # Sort segments by start date to ensure chronological order
                logger.debug("get_historical_data: Sorting and merging segment data...")
                merge_start = time.perf_counter()
                all_segment_data.sort(key=lambda x: x[0])
                
                # Flatten all data and sort by timestamp
                all_data = []
                for _, segment_data in all_segment_data:
                    all_data.extend(segment_data)
                
                # Sort by timestamp to ensure chronological order within segments
                all_data.sort(key=lambda x: x["timestamp"])
                merge_elapsed = time.perf_counter() - merge_start
                logger.info(f"get_historical_data: Data merged and sorted in {merge_elapsed:.3f}s (total records: {len(all_data)})")
                
                overall_elapsed = time.perf_counter() - overall_start_time
                logger.info(f"get_historical_data: COMPLETED in {overall_elapsed:.3f}s "
                           f"(broker_lookup: {broker_service_elapsed:.3f}s, split: {split_elapsed:.3f}s, "
                           f"parallel_fetch: {parallel_elapsed:.3f}s, merge: {merge_elapsed:.3f}s, "
                           f"segments: {len(segments)}, records: {len(all_data)})")
                
                return HistoricalData(all_data)
                
        except ApiException as e:
            overall_elapsed = time.perf_counter() - overall_start_time
            logger.error(f"get_historical_data: ApiException after {overall_elapsed:.3f}s: {e}")
            raise RuntimeError(f"Exception when calling Upstox API: {e}")
        except Exception as e:
            overall_elapsed = time.perf_counter() - overall_start_time
            logger.error(f"get_historical_data: Exception after {overall_elapsed:.3f}s: {e}")
            raise RuntimeError(f"Failed to fetch historical data: {e}")

    def api_instance(self):
        thread_id = threading.current_thread().name
        logger.debug(f"[{thread_id}] api_instance: Creating configuration...")
        
        config_start = time.perf_counter()
        configuration = upstox_client.Configuration(sandbox=False)
        
        token_start = time.perf_counter()
        configuration.access_token = AccessToken().get_token()
        token_elapsed = time.perf_counter() - token_start
        logger.debug(f"[{thread_id}] api_instance: Access token retrieved in {token_elapsed:.3f}s")
        
        configuration.verify_ssl = False
        api_instance = upstox_client.HistoryV3Api(upstox_client.ApiClient(configuration))
        
        config_elapsed = time.perf_counter() - config_start
        logger.debug(f"[{thread_id}] api_instance: Instance created in {config_elapsed:.3f}s (token: {token_elapsed:.3f}s)")
        return api_instance
