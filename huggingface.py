import os
from huggingface_hub import HfApi

api = HfApi()

api.upload_folder(
    folder_path="./Terrengganu",
    path_in_repo="Lawnet_Source/State/Terrengganu",
    repo_id="ytlailabs2024/malaysian_law",
    repo_type="dataset",
)