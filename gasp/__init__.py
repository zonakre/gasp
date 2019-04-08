"""
GASP Python Package
"""

def __import(full_path):
    """
    For 'gasp.apis.module', return the 'module' object
    """
    
    components = full_path.split('.')
    mod = __import__(components[0])
    
    for comp in components[1:]:
        mod = getattr(mod, comp)
    
    return mod


def exec_cmd(cmd):
    """
    Execute a command and provide information about the results
    """
    import subprocess
    
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    out, err = p.communicate()
    
    if p.returncode != 0:
        raise ValueError(
            'Output: {o}\nError: {e}'.format(o=str(out), e=str(err))
        )
    
    else:
        return out


def goToList(obj):
    """
    A method uses a list but the user gives a str
    
    This method will see if the object is a str and convert it to a list
    """
    
    return [obj] if type(obj) == str or type(obj) == unicode else \
           obj if type(obj) == list else None


def random_str(char_number, all_char=None):
    """
    Generates a random string with numbers and characters
    """
    
    import random as r
    import string
    
    char = string.digits + string.ascii_letters
    if all_char:
        char += string.punctuation
    
    rnd = ''
    
    for i in range(char_number): rnd += r.choice(char)
    
    return rnd


"""
Compress files with Python
"""


def tar_compress_folder(tar_fld, tar_file):
    """
    Compress a given folder
    """
    
    from gasp import exec_cmd
    
    cmd = 'cd {p} && tar -czvf {tar_f} {fld}'.format(
        tar_f=tar_file, fld=str(os.path.basename(tar_fld)),
        p=str(os.path.dirname(tar_fld))
    )
    
    code, out, err = exec_cmd(cmd)
    
    return tar_file


def zip_files(lst_files, zip_file):
    """
    Zip all files in the lst_files
    """
    
    import zipfile
    import os
    
    __zip = zipfile.ZipFile(zip_file, mode='w')
    
    for f in lst_files:
        __zip.write(f, os.path.relpath(f, os.path.dirname(zip_file)),
                       compress_type=zipfile.ZIP_DEFLATED)
    
    __zip.close()


def zip_folder(folder, zip_file):
    from gasp.oss import list_files
    
    files = list_files(folder)
    
    zip_files(files, zip_file)


"""
Operations with colors
"""

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(
        int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)
    )


def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


def idcolor_to_hex(rgbObj):
    """
    Find RGB in rgbObj and convert RGB to HEX
    """
    
    if type(rgbObj) == tuple or type(rgbObj) == list:
        _hex = rgb_to_hex(rgbObj[0], rgbObj[1], rgbObj[2])
    
    elif type(rgbObj) == dict:
        R = 'R' if 'R' in rgbObj else 'r' if 'r' in rgbObj else \
            None
        G = 'G' if 'G' in rgbObj else 'g' if 'g' in rgbObj else \
            None
        B = 'B' if 'B' in rgbObj else 'b' if 'b' in rgbObj else \
            None
        
        if not R or not G or not B:
            raise ValueError(
                ('rgbObj Value is not valid'
                 'You are using a dict to specify the color related with'
                 'each attribute categorie, but you are not using R, G and B'
                 ' as keys. Please use a dict with the following structure: '
                    '{\'R\': 255, \'R\': 255, \'R\': 255}'
                )
            )
        else:
            _hex = rgb_to_hex(rgbObj[R], rgbObj[G], rgbObj[B])
    
    elif type(rgbObj) == str or type(rgbObj) == unicode:
        _hex = rgbObj
    
    else:
        raise ValueError('rgbObj value is not valid')
    
    return _hex


"""
Datetime Objects Management
"""

def now_as_int():
    """
    Return Datetime.now as integer
    """
    
    import datetime
    
    _now = str(datetime.datetime.now())
    
    _now = _now.replace('-', '')
    _now = _now.replace(' ', '')
    _now = _now.replace(':', '')
    _now = _now.split('.')[0]
    
    return long(_now)


def day_to_intervals(interval_period):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    return [
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ...
    ]
    """
    
    import datetime
    
    MINUTES_FOR_DAY = 24 * 60
    NUMBER_INTERVALS = MINUTES_FOR_DAY / interval_period
    
    hour = 0
    minutes = 0
    INTERVALS = []
    
    for i in range(NUMBER_INTERVALS):
        __minutes = minutes + interval_period
        __interval = (
            (hour, minutes),
            (hour + 1 if __minutes >= 60 else hour,
             0 if __minutes == 60 else __minutes - 60 if __minutes > 60 else __minutes)
        )
        
        INTERVALS.append(__interval)
        minutes += interval_period
        
        if minutes == 60:
            minutes = 0
            hour += 1
        
        elif minutes > 60:
            minutes = minutes - 60
            hour += 1
    
    return INTERVALS


def day_to_intervals2(intervaltime):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    intervaltime = "01:00:00"
    
    return [
        ('00:00:00', '01:00:00'), ('01:00:00', '02:00:00'),
        ('02:00:00', '03:00:00'), ...,
        ('22:00:00', '23:00:00'), ('23:00:00', '23:59:00')
    ]
    """
    
    from datetime import datetime, timedelta
    
    TIME_OF_DAY = timedelta(hours=23, minutes=59, seconds=59)
    DURATION    = datetime.strptime(intervaltime, "%H:%M:%S")
    DURATION    = timedelta(
        hours=DURATION.hour, minutes=DURATION.minute,
        seconds=DURATION.second
    )
    
    PERIODS = []
    
    upperInt = timedelta(hours=0, minutes=0, seconds=0)
    
    while upperInt < TIME_OF_DAY:
        if not PERIODS:
            lowerInt = timedelta(hours=0, minutes=0, seconds=0)
        
        else:
            lowerInt = upperInt
        
        upperInt = lowerInt + DURATION
        
        PERIODS.append((
            "0" + str(lowerInt) if len(str(lowerInt)) == 7 else str(lowerInt),
            "0" + str(upperInt) if len(str(upperInt)) == 7 else str(upperInt)
        ))
    
    PERIODS[-1] = (PERIODS[-1][0], '23:59:59')
    
    return PERIODS

"""
Methods to deal with encoding problems
"""

def unicode_to_str(obj):
    """
    Transforms a unicode string into a regular string
    """
    
    import unicodedata
    
    return unicodedata.normalize('NFKD', obj).encode('ascii', 'ignore')


"""
Encripting strings
"""
def str_to_ascii(__str):
    """
    String to numeric code
    """
    
    return ''.join(str(ord(c)) for c in __str)


def id_encodefile(file__):
    """
    Find encoding of file using chardet
    """
    
    from chardet.universaldetector import UniversalDetector
    
    detector = UniversalDetector()
    
    for l in open(file__):
        detector.feed(l)
        
        if detector.done:
            break
    
    detector.close()
    
    return detector.result['encoding']


"""
Numbers utils
"""

def __round(n, n_digits):
    """
    Round n
    """
    
    dp = str(n).split('.')[1]
    
    mnt = str(int(dp[:n_digits]) + 1) if int(dp[n_digits]) >= 5 else dp[:n_digits]
    
    return int(n) + float('0.{}'.format(mnt))

