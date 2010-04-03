from __future__ import with_statement
import os, sys
from optparse import OptionParser, OptionGroup
import yaml
import logging
import time

from project import JSCCProject


def die(msg, code=-1):
    print >>sys.stderr, 'Error:', msg
    exit(code)

DEFAULT_PROJECT_FILENAME = 'jscc.yaml'


class Manager(object):
    def run(self, argv):
        parser = OptionParser(usage="%prog [options] [mode] [project]",
                              description='The jscc is a tool that helps you compile js code using google closure compiler.')
        
        mode_group = OptionGroup(parser, "Mode options (only specify one)")
        
        mode_group.add_option('-c', '--create', action='store_const', dest='mode', const='create', help='Create a new project.')
        mode_group.add_option('-u', '--update', action='store_const', dest='mode', const='update', help='Update the project. This is default mode.')
        mode_group.add_option('-w', '--watch', action='store_const', dest='mode', const='watch', help='Monitor the project for changes and update.')
        
        parser.add_option_group(mode_group)

        parser.add_option('--compiler', default='closure-compiler', help='Path to the google closure compiler. By default used: closure-compiler (see INSTALL for more details)')
        parser.add_option('-f', '--force', dest='force', action='store_true', help='Force recompile the project.')
        parser.add_option('-D', '--debug-mode', dest='debug_mode', action='store_true', help='Do not compile files. Just concatinate them.')
        parser.add_option('-d', '--debug', action='store_true', help='Display debug output')
                
        (options, args) = parser.parse_args(argv)
        if len(args) > 2:
            parser.error("incorrect number of arguments")

        self.compiler = options.compiler
        self.debug_mode = options.debug_mode or False
        force = options.force or False

        if options.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        mode = options.mode or 'update'
        project = args[1] if len(args) > 1 else DEFAULT_PROJECT_FILENAME
        getattr(self, mode)(project, force=force)
        
    def __get_project_filename(self, project):
        if project.find('.') == -1:
            project = '/'.join((project.rstrip('/ '), DEFAULT_PROJECT_FILENAME))
        return project, os.path.exists(project)               
        
    def create(self, project, **kwargs):
        filename, exists = self.__get_project_filename(project)
        
        if exists:
            die('Error: Can\'t create project. File "%s" is already exist.' % filename)
        
        def mkdir(d):
            if os.path.exists(d):
                return
            os.makedirs(d)
        root = os.path.dirname(filename) or '.'
        mkdir(root + '/src')
        mkdir(root + '/js')
        with open(filename, 'w') as f:
            print >>f, '''api_version: 1
source_dir: src
output_dir: js                            
default_compilation_level: simple         # possible values are: whitespace, simple and advanced

#targets:
#  output_filename-1.js:
#    compilation_level: advanced         # if specified, overwrites `default_compilation_level`
#    sources:                            # one or more sources
#      - input-1.1.js
#      - input-1.2.js
#      - input-1.3.js
#        
#  output_filename-2.js:
#    source: input-2.1.js                # only one source
#      
#  output_filename-3.js: input-3.1.js    # simplified notation
'''
        with open(filename, 'r') as f:
            try:
                JSCCProject(filename, yaml.load(f))
            except Exception, e:
                die(e)
           
    def update(self, project, **kwargs):
        filename, exists = self.__get_project_filename(project)
        if not exists:
            die("Project file doesn't exist: %s" % filename)
        with open(filename, 'r') as f:
            try:
                force = kwargs.get('force', False)
                logging.debug('Force: %s', force)
                p = JSCCProject(filename, yaml.load(f), compiler=self.compiler, debug_mode=self.debug_mode)
                if not force and p.is_valid(True):
                    print 'Project is up to date.'
                    return
                else:
                    p.make(force)
            except Exception, e:
                die(e)
   
    def watch(self, project, **kwargs):
        filename, exists = self.__get_project_filename(project)
        if not exists:
            die("Project file doesn't exist: %s" % filename)

        with open(filename, 'r') as f:
            try:
                p = JSCCProject(filename, yaml.load(f), compiler=self.compiler, debug_mode=self.debug_mode)
            except Exception, e:
                die(e)

        try:
            if kwargs.get('force'):
                p.make(True)
            
            greetings = True
            respect_project_mtime = True
            while True:
                if greetings:
                    print ">>> jscc is wating for changes. Press Ctrl-C to stop."
                    greetings = False
                if not p.is_valid(respect_project_mtime):
                    greetings = True
                    print "Sources changed. Recompiling..."
                    p.make()
                respect_project_mtime = False
                time.sleep(1)
        except Exception, e:
            die(e)
        except KeyboardInterrupt:
            print ''
