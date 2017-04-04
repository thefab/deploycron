# deploycron

A small tool for deploying crontab into your system.

It's useful if you want to deploy some crontab scripts into your system when you deploy your software that contains some extra crontab scripts.

# Install

```bash
pip install deploycron
```

# Usage

There are two functions in the package now,

```python
def deploycron(filename="", content="", override=False):
```

> Install crontabs into the system if it's not installed.  
> This will not remove the other crontabs installed in the system if not specified  
> as override. It just merge the new one with the existing one.  
> If you provide `filename`, then will install the crontabs in that file  
> otherwise install crontabs specified in content  
> 
> `filename` - file contains crontab, one crontab for a line  
> `content`  - string that contains crontab, one crontab for a line  
> `override` - override the origin crontab  

Example: 

```python
from deploycron import deploycron

# specify a filename
deploycron(filename="/tmp/youcrontab.tab")

# or just specify crontab content
deploycron(content="* * * * * echo hello > /tmp/hello")

# if you want to overwrite the existing crontab, set `override` to True
deploycron(content="* * * * * echo hello > /tmp/hello", override=True)
```

and 

```python
def undeploycron_between(start_line, stop_line, occur_start, occur_stop):
```

> Uninstall crontab parts between two lines (included).
> If the start_line or the stop_line is not found into the installed crontab,
> it won't be modified.
> Returns `True` if the operation succeded and `False` if the operation failed.
>
>
> `start_line` - start crontab line (the actual line, not the line number) to delimit the crontab block to remove  
> `stop_line` - stop crontab line (the actual line, not the line number) to delimit the crontab block to remove  
> `occur_start` - number of the occurrence of `start_line` at which the uninstall will start (1 => first occurrence)  
> `occur_start` - number of the occurrence of `stop_line` at which the uninstall will stop  

Example 1:
```python
from deploycron import deploycron

# Crontab sample
deploycron(content="* * * * * echo Good > /tmp/buffer")
deploycron(content="* * * * * echo day > /tmp/buffer")
deploycron(content="* * * * * echo to > /tmp/buffer")
deploycron(content="* * * * * echo you > /tmp/buffer")
deploycron(content="* * * * * echo mate > /tmp/buffer")

# We want to remove from line 2 to line 4 included
undeploycron_between("* * * * * echo day > /tmp/buffer",
                     "* * * * * echo mate > /tmp/buffer")
```

With this script, we first get a crontab like this one :

    * * * * * echo Good > /tmp/buffer
    * * * * * echo day > /tmp/buffer
    * * * * * echo to > /tmp/buffer
    * * * * * echo you > /tmp/buffer
    * * * * * echo mate > /tmp/buffer
    
And then, after the undeploycron_between(), we get :

    * * * * * echo Good > /tmp/buffer
    * * * * * echo mate > /tmp/buffer

Example 2:
```python
from deploycron import deploycron

# Crontab sample
deploycron(content="* * * * * echo Good > /tmp/buffer")
deploycron(content="* * * * * echo day > /tmp/buffer")
deploycron(content="* * * * * echo to > /tmp/buffer")
deploycron(content="* * * * * echo you > /tmp/buffer")
deploycron(content="* * * * * echo mate > /tmp/buffer")
deploycron(content="* * * * * echo Good > /tmp/buffer")
deploycron(content="* * * * * echo to > /tmp/buffer")
deploycron(content="* * * * * echo see > /tmp/buffer")
deploycron(content="* * * * * echo you > /tmp/buffer")

# We want to remove from line 6 to line 9 included
undeploycron_between("* * * * * echo Good > /tmp/buffer",
                     "* * * * * echo you > /tmp/buffer",
                     2,
                     2)
```

This script allows us to go from this crontab :

    * * * * * echo Good > /tmp/buffer
    * * * * * echo day > /tmp/buffer
    * * * * * echo to > /tmp/buffer
    * * * * * echo you > /tmp/buffer
    * * * * * echo mate > /tmp/buffer
    * * * * * echo Good > /tmp/buffer
    * * * * * echo to > /tmp/buffer
    * * * * * echo see > /tmp/buffer
    * * * * * echo you > /tmp/buffer

To this one :

    * * * * * echo Good > /tmp/buffer
    * * * * * echo day > /tmp/buffer
    * * * * * echo to > /tmp/buffer
    * * * * * echo you > /tmp/buffer
    * * * * * echo mate > /tmp/buffer

The undeploy doesn't trigger at the first occurrence of the lines here. Instead, it triggers at the second occurrence of both `start_line` and `stop_line` as precised in the parameters.

## CLI scripts

The package also provides two helpers CLI scripts mapped to corresponding functions:

```
usage: deploycron_file [-h] filepath

positional arguments:
  filepath    Complete file path of the cron to deploy

optional arguments:
  -h, --help  show this help message and exit
```

and

```
usage: undeploycron_between [-h] start_line stop_line

positional arguments:
  start_line  start line to delimit the crontab block to remove
  stop_line   stop line to delimit the crontab block to remove

optional arguments:
  -h, --help  show this help message and exit
```

## Note

Only support in unix-like system, eg. Linux/Mac

## Author

* Monklof (monklof@gmail.com)

## License

MIT
