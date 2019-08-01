![](https://img.shields.io/pypi/v/foliantcontrib.mermaid.svg)

# Mermaid Diagrams Preprocessor for Foliant

[Mermaid](https://mermaidjs.github.io/) is an open source diagram visualization tool. This preprocessor converts Mermaid diagram definitions in the your Markdown files into images on the fly during project build.

## Installation

```bash
$ pip install foliantcontrib.mermaid
```

Please not that to use this preprocessor you will also need to install Mermaid and Mermaid CLI:

```bash
$ npm install mermaid # installs locally
$ npm install mermaid.cli
```

## Config

To enable the preprocessor, add `mermaid` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - mermaid
```

The preprocessor has a number of options:

```yaml
preprocessors:
    - mermaid:
        cache_dir: !path .diagramscache
        mermaid_path: !path node_modules/.bin/mmdc
        format: svg
        params:
            ...
```

`cache_dir`
:   Path to the directory with the generated diagrams. It can be a path relative to the project root or a global one; you can use `~/` shortcut.

> To save time during build, only new and modified diagrams are rendered. The generated images are cached and reused in future builds.

`mermaid_path`
:   Path to Mermaid CLI binary. If you installed Mermaid locally this parameter is required. Default: `mmdc`.

`format`
:   Generated image format. Available: `svg`, `png`, `pdf`. Default `svg`.

`params`
:   Params passed to the image generation command:

        preprocessors:
            - mermaid:
                params:
                    theme: forest

> To see the full list of available params, run `mmdc -h` or check [here](https://github.com/mermaidjs/mermaid.cli#options).

## Usage

To insert a diagram definition in your Markdown source, enclose it between `<<mermaid>...</mermaid>` tags:

```markdown
Here’s a diagram:

<<mermaid>
graph TD;
    A-->B;
</mermaid>
```

You can set any parameters in the tag options. Tag options have priority over the config options so you can override some values for specific diagrams while having the default ones set up in the config.

Tags also have an exclusive option `caption` — the markdown caption of the diagram image.

```markdown
Diagram with a caption:

<<mermaid caption="Deployment diagram"
          params="theme: dark">
</mermaid>
```

> Note that command params listed in the `params` option are stated in YAML format. Remember that YAML is sensitive to indentation so for several params it is more suitable to use JSON-like mappings: `{key1: 1, key2: 'value2'}`.
