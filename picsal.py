import exif
import datetime as dt
import os
import shutil
from typing import Dict, List

class TimeRange:
    __start: dt.datetime
    __end: dt.datetime

    def __init__(self, start: dt.datetime, end: dt.datetime):
        self.__start = start
        self.__end = end

    def __contains__(self, time: dt.datetime) -> bool:
        return time >= self.__start and time <= self.__end

    def overlaps(self, other: 'TimeRange'):
        return ((self.__start <= other.__start and self.__end > other.__start)
               or other.__start <= self.__start and other.__end > self.__start)

class Category:
    __name: str
    __ranges: List[TimeRange] = []

    def __init__(self, name: str):
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    def add_range(self, new_range: TimeRange) -> bool:
        if any(rng.overlaps(new_range) for rng in self.__ranges):
            return False
        self.__ranges.append(new_range)
        return True

    def __contains__(self, time: dt.datetime) -> bool:
        return any(time in rng for rng in self.__ranges)
        
class File:
    __path: str
    __name: str
    __date: dt.datetime

    def __init__(self, path: str, name: str, date: dt.datetime):
        self.__path = path
        self.__name = name
        self.__date = date

    def get_full_path(self) -> str:
        return '/'.join([self.__path, self.__name])

    def get_date(self) -> dt.datetime:
        return self.__date

def get_exif_datetime(path: str) -> dt.datetime:
    with open(path, 'rb') as img_file:
        image = exif.Image(img_file)
    if not image.has_exif or not image.datetime:
        return None
    date, time = image.datetime.split(" ")
    date = date.replace(':', '-')
    isotime = '-'.join([date, time])
    return dt.datetime.fromtimestamp(isotime)

def create_filename(old_filename: str, time: dt.datetime, config: {}) -> str:
    old_name, extension = os.path.splitext(old_filename)
    filename: str = ''
    if config.get('prepend_timestamp', 'false') == 'true':
        filename += f'{time}'.replace(':', '-').replace(' ', '_')
    
    if config.get('keep_filename', 'false') == 'true':
        if filename: 
            filename += '_'
        filename += old_name

    if not filename:
        raise Exception((f'cannot create timestamp from '
                'filename {old_filename}, datetime {time}, config "{config}"'))

    filename += extension
    return filename

def get_files(directory: str, config: {}) -> List[str]:
    if not os.path.isdir(directory):
        raise Exception(f'{directory} is not a directory.')

    extensions: str = config.get('extensions')
    if not extensions:
        raise Exception('no extensions provided in config.')

    return [filename for filename in os.listdir(directory) 
                if os.path.splitext(filename)[1] in extensions]

def create_target_dir_name(time: dt.datetime, ranges: List[TimeRange], config: {}) -> str:
    target_path = ''
    for range in ranges:
        if time in range:
            target_path = range.get_name()
            break

    if not target_path:
        target_path = f'{time.year:04}-{time.month:02}'

    target_path = os.path.join(config['target_dir'], target_path) 
    return target_path

def get_files_recurse(dir: str, extensions: List[str]) -> List[str]:
    if not os.path.isdir(dir):
        raise Exception(f"'{dir} is not a directory")

    files: List[str] = []

    for elem in os.listdir(dir):
        if os.path.isdir(elem):
            files += get_files_recurse(os.path.join(dir, elem), extensions)
        elif os.path.splitext(elem)[1] in extensions:
            files.append(os.path.join(dir, elem))

    return files


if __name__ == "__main__":
    config = {
        'prepend_timestamp': 'true',
        'keep_filename' : 'false',
        'target_dir' : '',
        'source_dir' : '',
        'extensions' : ['.jpg', '.jpeg', '.JPG', '.JPEG']}

    files = get_files_recurse(config.get('source_dir', ''), config.get('extensions', []))

    for source in files:
        time: dt.datetime = (
            get_exif_datetime(source) or 
            dt.datetime.fromtimestamp(os.path.getctime(source)))

        target_name = create_filename(os.path.basename(source), time, config)
        target_dir = create_target_dir_name(time, [], config)
        target_dir = os.path.join(config['target_path'], target_dir)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        target = os.path.join(target_dir, target_name)
        if os.path.exists(target):
            continue

        shutil.copy(source, target)





        

    

