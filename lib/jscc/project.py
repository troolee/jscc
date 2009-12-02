import os
import itertools
import logging
from datetime import datetime
from subprocess import call

COMPILATION_LEVELS = {
    'whitespace': 'WHITESPACE_ONLY',
    'simple': 'SIMPLE_OPTIMIZATIONS',
    'advanced': 'ADVANCED_OPTIMIZATIONS',
}


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
            if 'source' in data:
                self.sources = [data.pop('source')]
        else:
            raise Exception('Unsupported notation of the target %s.' % target)
            
    def get_target_filename(self):
        return '/'.join((self.project.output_dir, self.target))
            
    def get_source_filename(self, source):
        return '/'.join((self.project.source_dir, source))
            
    def is_valid(self, respect_project_mtime=False):
        logging.debug('Checking target %s', self.target)
        if not os.path.exists(self.get_target_filename()):
            logging.debug('Need to be updated: output not found')
            return False
        target_ctime = os.path.getctime(self.get_target_filename())
        if respect_project_mtime:
            project_mtime = os.path.getmtime(self.project.filename)
            if project_mtime > target_ctime:
                logging.debug('Need to be updated: Project file changed')
                return False
        for s in self.sources:
            mtime = os.path.getmtime(self.get_source_filename(s))
            if mtime > target_ctime:
                logging.debug('Need to be updated: Source %s changed' % s)
                return False
        logging.debug('Up to date')
        return True
    
    def make(self):
        if not self.project.compiler:
            raise Exception('Compiler is not specified.')
        if not self.sources:
            return
        
        if self.is_valid():
            return
        print '%s...' % self.target
        
        def get_cmd(*args):
            args = list(args)
            args.insert(0, self.project.compiler)
            return args
            
        def get_source_args(list):
            for s in list:
                yield '--js'
                yield self.get_source_filename(s)
        
        cmd = get_cmd('--js_output_file', self.get_target_filename(),
                      '--compilation_level', COMPILATION_LEVELS[self.compilation_level],
                      *tuple(get_source_args(self.sources)))
        logging.debug('>>> ' + ' '.join(cmd))
        call(cmd)
            

class JSCCProject:
    def __init__(self, filename, data, compiler=None):
        self.filename = filename
        self.root_path = '/'.join(os.path.abspath(filename).split('/')[:-1])
        
        self.compiler = compiler
        self.api_version = data.pop('api_version', '1')
        if self.api_version != 1:
            raise Exception('Unsupported api version: %s' % self.api_version)
        self.source_dir = self.root_path + '/' + data.pop('source_dir', 'src')
        self.output_dir = self.root_path + '/' + data.pop('output_dir', 'js')
        self.default_compilation_level = data.pop('default_compilation_level', 'simple')
        if self.default_compilation_level not in ['whitespace', 'simple', 'advanced']:
            raise Exception('Unsupported level of compilation: %s' % self.default_compilation_level)
        self.targets = []
        for target_data in data.pop('targets', {}).items():
            self.targets.append(JSCCTarget(self, *target_data))
        
        if len(data):
            raise Exception('Unsupported option(s): %s' % ', '.join(data.keys()))

    def is_valid(self, respect_project_mtime=False):
        for target in self.targets:
            if not target.is_valid(respect_project_mtime):
                return False
        return True
    
    def make(self):
        for target in self.targets:
            target.make()
