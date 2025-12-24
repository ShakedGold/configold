# CONFIGOLD
Like gold, you configuration should be precious but malleable

### Configure your shell easily with an easy to use user interface
![textual-ui.png](./media/textual-ui.png)
![textual-ui-aliases-list.png](./media/textual-ui-aliases-list.png)

**All in the shell!**

An easy to use user interface to easily configure your setup.

Don't like to change defaults? just nextify that shi- and get a great configuration by default!

### Create custom scripts to install and configure
Don't like the options you have in the UI?

You can create a custom script that will install whatever program you want and create a custom script to configure it automatically!

```python
import asyncio
from pathlib import PosixPath
from apps.zsh import ZshApp, ZshConfigData
from utils import setup_logger


zsh_config = ZshConfigData(
    aliases=dict(configold='echo "THE BEST CONFIGURATION LIBRARY"'),
)
zsh = ZshApp(zsh_config)


async def main() -> None:
    setup_logger()

    did_install = await zsh.install()
    did_configure = zsh_config.config()

    print(f"Did install zsh: {did_install}")
    print(f"Did configure zsh: {did_configure}")


if __name__ == "__main__":
    asyncio.run(main())
```

The output `.zshrc`:
```bash

# This is the exports, they define variables that are accessible by other programs (plus the shell itself)
# You can override this to whatever you want, for example: the EDITOR env variable will define what multiple programs
# will use as their editor, for example `sudoedit` (the command to edit files as the super user)
export EDITOR="`which nvim`"


# This is the aliases, they define 'commands' that will point to other commands themself, for example: A `g` alias is just an alias to `git`
alias configold="echo \"THE BEST CONFIGURATION LIBRARY\""
```

You can share these scripts with friends to create your own library and default configurations!

# Building
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

In order to run:
```bash
python main.py
```
