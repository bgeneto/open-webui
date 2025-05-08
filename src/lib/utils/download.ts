// Utility to map language names to file extensions for download
export function getExtension(lang: string | undefined): string {
    if (!lang) return 'md';
    const map: Record<string, string> = {
        python: 'py', py: 'py',
        c: 'c',
        cpp: 'cpp', 'c++': 'cpp', cc: 'cpp',
        fortran: 'f90', f90: 'f90',
        js: 'js', javascript: 'js',
        ts: 'ts', typescript: 'ts',
        html: 'html',
        css: 'css',
        scss: 'scss',
        less: 'less',
        csv: 'csv',
        tsv: 'tsv',
        svg: 'svg',
        latex: 'tex', tex: 'tex',
        bash: 'sh', sh: 'sh', shell: 'sh', zsh: 'sh', ksh: 'sh', fish: 'fish',
        powershell: 'ps1', ps1: 'ps1', pwsh: 'ps1',
        bat: 'bat', batch: 'bat', cmd: 'bat',
        md: 'md', markdown: 'md',
        json: 'json',
        yaml: 'yaml', yml: 'yml',
        ini: 'ini',
        conf: 'conf',
        log: 'log',
        xml: 'xml',
        makefile: 'mak', mk: 'mak',
        dockerfile: 'dockerfile',
        go: 'go', golang: 'go',
        rb: 'rb', ruby: 'rb',
        php: 'php',
        java: 'java',
        kt: 'kt', kotlin: 'kt',
        swift: 'swift',
        scala: 'scala',
        dart: 'dart',
        r: 'r',
        sas: 'sas',
        sql: 'sql',
        tcl: 'tcl',
        vb: 'vb', vba: 'vba', vbnet: 'vb',
        groovy: 'groovy',
        clj: 'clj', clojure: 'clj',
        elixir: 'ex', ex: 'ex', exs: 'exs',
        erlang: 'erl', erl: 'erl',
        fsharp: 'fs', fs: 'fs', 'f#': 'fs',
        haskell: 'hs', hs: 'hs',
        ocaml: 'ml', ml: 'ml',
        coffee: 'coffee', coffeescript: 'coffee',
        perl: 'pl', pl: 'pl', pm: 'pm',
        rs: 'rs', rust: 'rs',
        lua: 'lua',
        asm: 'asm', nasm: 'asm', gas: 's', s: 's',
        objectivec: 'm', objc: 'm', objcpp: 'mm', objectivecpp: 'mm',
        prolog: 'pl',
        pascal: 'pas',
        d: 'd',
        abap: 'abap',
        apex: 'apex',
        arduino: 'ino',
        awk: 'awk',
        crystal: 'cr',
        elm: 'elm',
        gherkin: 'feature',
        graphql: 'graphql',
        julia: 'jl',
        lisp: 'lisp', el: 'el', emacs: 'el',
        matlab: 'm',
        nim: 'nim',
        nix: 'nix',
        raku: 'raku', perl6: 'raku',
        restructuredtext: 'rst', rst: 'rst',
        sass: 'sass',
        smalltalk: 'st',
        solidity: 'sol',
        verilog: 'v', vhdl: 'vhd',
        zig: 'zig',
        // ...add more as needed
    };
    return map[lang.toLowerCase()] || 'md';
}

export function downloadCode(code: string, lang: string | undefined) {
    const ext = getExtension(lang);
    const filename = `codeblock.${ext}`;
    const blob = new Blob([code], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }, 0);
}
