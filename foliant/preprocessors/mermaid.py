'''
GraphViz diagrams preprocessor for Foliant documenation authoring tool.
'''

import re

from pathlib import Path, PosixPath
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.utils.combined_options import (Options,
                                                          CombinedOptions)
from foliant.preprocessors.utils.preprocessor_ext import (BasePreprocessorExt,
                                                          allow_fail)

OptionValue = int or float or bool or str


class Preprocessor(BasePreprocessorExt):
    defaults = {
        'cache_dir': Path('.diagramscache'),
        'format': 'svg',
        'params': {}
    }
    tags = ('mermaid',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Options(self.options,
                              defaults=self.defaults)

        self._cache_path = self.project_path / self.config['cache_dir']

        self.logger = self.logger.getChild('mermaid')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _get_command(self,
                     options: CombinedOptions or dict,
                     diagram_src_path: PosixPath,
                     diagram_path: PosixPath) -> str:
        '''Generate the image generation command.

        :param options: a CombinedOptions object with tag and config options
        :param diagram_src_path: Path to the diagram source file
        :param diagram_path: Path to the diagram output file

        :returns: Complete image generation command
        '''

        components = ['mmdc']

        components.append(f'-i {diagram_src_path}')
        components.append(f'-o {diagram_path}')

        for param_name, param_value in options['params'].items():
            if len(param_name) == 1:
                components.append(f'-{param_name} {param_value}')
            else:
                components.append(f'--{param_name} {param_value}')

        return ' '.join(components)

    @allow_fail('Error while processing mermaid tag.')
    def _process_diagrams(self, block) -> str:
        '''
        Process mermaid tag.
        Save Mermaid diagram body to .mmd file, generate an image from it,
        and return the image ref.

        If the image for this diagram has already been generated, the existing version
        is used.

        :returns: Image ref
        '''
        tag_options = Options(self.get_options(block.group('options')))
        options = CombinedOptions({'config': self.options,
                                   'tag': tag_options},
                                  priority='tag')
        body = block.group('body')

        self.logger.debug(f'Processing Mermaid diagram, options: {options}, body: {body}')

        body_hash = md5(f'{body}'.encode())
        body_hash.update(str(options.options).encode())

        diagram_src_path = self._cache_path / 'mermaid' / f'{body_hash.hexdigest()}.mmd'

        self.logger.debug(f'Diagram definition file path: {diagram_src_path}')

        diagram_path = diagram_src_path.with_suffix(f'.{options["format"]}')

        self.logger.debug(f'Diagram image path: {diagram_path}')

        if diagram_path.exists():
            self.logger.debug('Diagram image found in cache')

            return f'![{config.get("caption", "")}]({diagram_path.absolute().as_posix()})'

        diagram_src_path.parent.mkdir(parents=True, exist_ok=True)

        with open(diagram_src_path, 'w', encoding='utf8') as diagram_src_file:
            diagram_src_file.write(body)

            self.logger.debug(f'Diagram definition written into the file')

        try:
            command = self._get_command(options, diagram_src_path, diagram_path)
            self.logger.debug(f'Constructed command: {command}')
            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            self.logger.debug(f'Diagram image saved')

        # except CalledProcessError as e:
        #     self._warning('Processing of Mermaid diagram failed.',
        #                   context=self.get_tag_context(block),
        #                   error=e)
        #     return block.group(0)
        return self._get_result(diagram_path, options)

    def apply(self):
        self._process_tags_for_all_files(self._process_diagrams)
        self.logger.info('Preprocessor applied')
