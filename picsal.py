import exif
import filecmp
import datetime as dt
import os
import re
import shutil
from typing import Dict, List
import config

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
    if not image.has_exif or 'datetime' not in dir(image):
        print(f"image '{path}' has no datetime")
        return None
    return dt.datetime.strptime(image.datetime, '%Y:%m:%d %H:%M:%S')

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

def increment_filename(filename: str) -> str:
    name, extension = os.path.splitext(filename)
    count = re.findall('.*_([0-9]+)$', name)
    if count:
        number = int(count[0]) + 1
        return name[:-len(count[0])] + "{:02}".format(number) + extension
    else:
        return f'{name}_00{extension}'

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

def move(target: str, source:str, copy) -> None:
    while os.path.exists(target):
        if filecmp.cmp(target, source):
            print(f"skipping file '{source}': file exists in target folder'")
            return
        else:
            target = increment_filename(target)
    
    if copy:
        shutil.copy2(source, target)
    else:
        shutil.move(source, target)
    

if __name__ == "__main__":

    conf = config.init_config()
    
    files = get_files_recurse(conf.get('source_dir', ''), conf.get('extensions', []))

    for source in files:
        time: dt.datetime = (
            get_exif_datetime(source) or 
            dt.datetime.fromtimestamp(os.path.getctime(source)))

        target_name = create_filename(os.path.basename(source), time, conf)
        target_dir = create_target_dir_name(time, [], conf)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        target = os.path.join(target_dir, target_name)
        copy = conf.get('copy', False)
        move(target, source, copy)
