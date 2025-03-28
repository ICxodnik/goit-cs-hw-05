import argparse
import asyncio
import os
import logging
import aioshutil
import aiopath

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def read_folder(folder_path):
    file_paths = []
    try:
        folder = aiopath.AsyncPath(folder_path)
        async for file in folder.rglob("*"):
            if await file.is_file():
                file_paths.append(file.relative_to(folder_path).as_posix())
            
    except Exception as e:
        logger.error(f"Error reading folder {folder_path}. Nothing to copy.")
    return file_paths

async def copy_file(from_path, to_path):
    logger.info(f"Copying {from_path} to {to_path}")
    try:
        path = aiopath.AsyncPath(to_path)
        await path.mkdir(parents=True, exist_ok=True)
        await aioshutil.copy2(from_path, to_path)
    except Exception as e:
        logger.error(f"Error copying {from_path} to {to_path}", e)
    
def flatten_to_dir_type(file_path: str):
    path, ext = os.path.splitext(file_path)
    
    # build new name to not override existing files in output directory
    path_parts = path.split('/')
    for index, part in enumerate(path_parts[:-1]):
        path_parts[index] = part[0]
        
    new_name = ''.join(path_parts) + ext
    
    return (ext[1:], new_name)
    
async def main():
    parser = argparse.ArgumentParser(description='Copy files from source directory to target directory')
    parser.add_argument('--id', type=str, help='Source directory')
    parser.add_argument('--od', type=str, help='Target directory')
    args = parser.parse_args()
    
    path = aiopath.AsyncPath(args.od)
    await path.mkdir(parents=True, exist_ok=True)
    
    files = await read_folder(args.id)
    
    tasks = []
    for file in files:
        ext, new_name = flatten_to_dir_type(file)
        target_path = os.path.join(args.od, ext, new_name)
        tasks.append(copy_file(os.path.join(args.id, file), target_path))
        
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
