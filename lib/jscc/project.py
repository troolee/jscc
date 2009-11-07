import os


class JSCCTarget:
    def __init__(self, project, target, data):
        self.project = project
        self.target = target
        if isinstance(data, str):
            self.compilation_level = project.default_compilation_level
            self.sources = [data]
        elif isinstance(data, dict):
            self.compilation_level = data.pop('compilation_level', project.default_compilation_level)
            if 'source' in data and 'sources' in data:
                raise Exception('Please specify only one of options `source` or `sources` for the target %s.' % target)
            if 'source' in data:
                s = data.pop('source')
                if not isinstance(s, (str, unicode)):
                    raise Exception('Option source must be a string for the target %s.' % target)
                self.sources = [s]
            else:
                self.sources = data.pop('sources')
                if not isinstance(self.sources, (list, tuple)):
                    raise Exception('Sources must be a list of string for the target %s.' % target)
            self.sources.append(data.pop('source', None))
            if 'source' in data:
                self.sources = [data.pop('source')]
        else:
            raise Exception('Unsupported notation of the target %s.' % target)
            
    def get_target_filename(self):
        return '/'.join((self.project.source_dir, self.target))
            
    def __get_source_filename(self, source):
        return '/'.join((self.project.source_dir, source))
            
    def is_valid(self):
        if not os.path.exists(self.get_target_filename()):
            return False
        return True
    
    def make(self):
        pass
            

class JSCCProject:
    def __init__(self, data):
        self.api_version = data.pop('api_version', '1')
        if self.api_version != 1:
            raise Exception('Unsupported api version: %s' % self.api_version)
        self.source_dir = data.pop('source_dir', 'src')
        self.output_dir = data.pop('output_dir', 'js')
        self.default_compilation_level = data.pop('default_compilation_level', 'simple')
        if self.default_compilation_level not in ['whitespace', 'simple', 'advanced']:
            raise Exception('Unsupported level of compilation: %s' % self.default_compilation_level)
        self.targets = []
        for target_data in data.pop('targets', {}).items():
            self.targets.append(JSCCTarget(self, *target_data))
        
        if len(data):
            raise Exception('Unsupported option(s): %s' % ', '.join(data.keys()))

    def is_valid(self):
        for target in self.targets:
            if not target.is_valid():
                return False
        return True
    
    def make(self):
        for target in self.targets:
            target.make()
