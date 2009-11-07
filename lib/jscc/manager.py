from optparse import OptionParser, OptionGroup


class Manager(object):
    def run(self, argv):
        parser = OptionParser(usage="%prog [mode] [project]",
                              description='The jscc is a tool that helps you compile js code using google closure compiler.')
        
        mode_group = OptionGroup(parser, "Mode options (only specify one)")
        
        mode_group.add_option('-c', '--create', action='store_const', dest='mode', const='create', help='Create a new project.')
        mode_group.add_option('-u', '--update', action='store_const', dest='mode', const='update', help='Update the project. This is default mode.')
        mode_group.add_option('-w', '--watch', action='store_const', dest='mode', const='watch', help='Monitor the project for changes and update.')
        
        parser.add_option_group(mode_group)
                
        (options, args) = parser.parse_args(argv)
        if len(args) > 1:
            parser.error("incorrect number of arguments")

        mode = options.mode or 'update'
        project = args[0] if len(args) > 0 else 'jscc.yml'
        getattr(self, mode)(project)
        
    def create(self, project):
        pass
   
    def update(self, project):
        pass
   
    def watch(self, project):
        print ">>> jscc is wathing for changes. Press Ctrl-C to stop."
