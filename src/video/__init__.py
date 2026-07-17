# El pipeline (process_video) requiere las dependencias CV de
# requirements-video.txt — se importa adentro de las funciones para que
# schema y validation funcionen sin ellas.
from src.video.schema import (
    save_tracking, load_tracking, validate_positions_df, empty_positions_df,
)
from src.video.validation import (
    track_summary, players_per_frame, compare_with_lineups, positions_plausibility,
)
from src.video.pipeline import check_environment, environment_ready, process_video
from src.video.downloader import (
    capture_stream_url, download_stream, download_match_video,
)
