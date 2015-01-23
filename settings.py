import os
import ConfigParser

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

try:
    import arcpy
except:
    # fake it till you make it; an attribute dictionary for arcpy.env
    arcpy = AttrDict()

    cfg_path = os.path.join(os.environ['HOME'], '.config', 'btm')
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)
 
    arcpy.env = AttrDict({
        'overwriteOutput': True,
        'scratchWorkspace': cfg_path,
        'workspace': cfg_path,
        'addOutputsToMap': True
    })
    
class Settings(object):
    """
    A settings manager. Keeps application-specific configuration
    managed in an INI file sycronized with application settings.
    """

    def __init__(self, app_name):
        """Initialize settings state."""
        self.app_name = app_name
        self.app_dir = os.path.join(self._base_dir(), app_name)
        self.cfg_file = os.path.join(
            self.app_dir, '{}.cfg'.format(app_name))
        # a dictionary of settings
        self.defaults = {
            'overwriteOutput': arcpy.env.overwriteOutput,
            'scratchWorkspace': os.path.join(self.app_dir, 'scratch'),
            'workspace': os.path.join(self.app_dir, 'scratch'),
            'addOutputsToMap': arcpy.env.addOutputsToMap 
        }
        self.cfg = self._init_config()
        self.settings = self._settings()

    def update(self, key, value):
        """Update a setting."""
        self.cfg.set(self.app_name, key, str(value))
        with open(self.cfg_file, 'wb') as config_file:
            self.cfg.write(config_file)
        # update base settings
        self.settings = self._settings()

    def _init_config(self):
        """Initialize a basic configuration file from scratch."""
        settings = None
        if not os.path.exists(self.cfg_path):
            # recursively create a config directory
            if not os.path.exists(self.app_dir):
                os.makedirs(self.app_dir)
            cfg = self._write_defaults()
        else:
            cfg = self._read_settings()
        return cfg

    def _settings(self):
        """
        Dump settings to a attribute dictionary, attributes can then be 
        accessed with the dot method insetad of explicit dictionary item names.
        """
        settings = None 
        if self.cfg:
            section = self.cfg._sections[self.app_name] 
            settings = AttrDict(section)
        return settings
    
    def _read_settings(self):
        """Read to configuration file."""
        cfg = ConfigParser.SafeConfigParser()
        cfg.read(self.cfg_path)
        return cfg
 
    def _write_defaults(self):
        """Write defaults to configuration file."""
        cfg = ConfigParser.SafeConfigParser()

        cfg.read(self.cfg_path)
        cfg.add_section(self.app_name)
        for (var, val) in self.defaults.items():
            cfg.set(app_name, var, str(val))
        with open(self.cfg_path, 'wb') as config_file:
            cfg.write(config_file)
        return cfg
 
    def _base_dir(self):
        """An application-specific directory."""
        if 'APPDATA' in os.environ:
            base = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            base = os.environ['XDF_CONFIG_HOME']
        else:
            base = os.path.join(os.environ['HOME'], '.config')
        return base 

app_name = 'btm'
s = Settings(app_name)

# set up a location for logging
# TODO use this
log_path = os.path.join(s.app_dir, '{}.log'.format(app_name))
