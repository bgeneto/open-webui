// Utility to map language names to file extensions for download
export function getExtension(lang: string | undefined): string {
    if (!lang) return 'md';
    const map: Record<string, string> = {
        abap: 'abap',
        apex: 'apex',
        arduino: 'ino',
        asm: 'asm', gas: 's', s: 's',
        awk: 'awk',
        bash: 'sh', sh: 'sh', shell: 'sh', zsh: 'sh', ksh: 'sh', fish: 'fish',
        bat: 'bat', batch: 'bat', cmd: 'bat',
        c: 'c',
        clj: 'clj', clojure: 'clj',
        coffee: 'coffee', coffeescript: 'coffee',
        conf: 'conf',
        cpp: 'cpp', 'c++': 'cpp', cc: 'cpp',
        crystal: 'cr',
        csv: 'csv',
        d: 'd',
        dart: 'dart',
        dockerfile: 'dockerfile',
        el: 'el', emacs: 'el',
        elixir: 'ex', ex: 'ex', exs: 'exs',
        elm: 'elm',
        erlang: 'erl', erl: 'erl',
        feature: 'feature', // gherkin
        fortran: 'f90', f90: 'f90',
        fs: 'fs', fsharp: 'fs', 'f#': 'fs',
        gherkin: 'feature',
        go: 'go', golang: 'go',
        graphql: 'graphql',
        groovy: 'groovy',
        haskell: 'hs', hs: 'hs',
        html: 'html',
        ini: 'ini',
        java: 'java',
        javascript: 'js', js: 'js',
        jl: 'jl', julia: 'jl',
        json: 'json',
        kotlin: 'kt', kt: 'kt',
        latex: 'tex', tex: 'tex',
        less: 'less',
        lisp: 'lisp',
        log: 'log',
        lua: 'lua',
        mak: 'mak', makefile: 'mak', mk: 'mak',
        markdown: 'md', md: 'md',
        matlab: 'm',
        ml: 'ml', ocaml: 'ml',
        nasm: 'asm',
        nim: 'nim',
        nix: 'nix',
        objectivec: 'm', objc: 'm', objcpp: 'mm', objectivecpp: 'mm',
        pascal: 'pas',
        perl: 'pl', pl: 'pl', pm: 'pm',
        perl6: 'raku', raku: 'raku',
        php: 'php',
        powershell: 'ps1', ps1: 'ps1', pwsh: 'ps1',
        prolog: 'pl',
        python: 'py', py: 'py',
        r: 'r',
        restructuredtext: 'rst', rst: 'rst',
        rb: 'rb', ruby: 'rb',
        rs: 'rs', rust: 'rs',
        sass: 'sass',
        sas: 'sas',
        scala: 'scala',
        scss: 'scss',
        smalltalk: 'st',
        solidity: 'sol',
        sql: 'sql',
        svelte: 'svelte',
        svg: 'svg',
        swift: 'swift',
        tcl: 'tcl',
        ts: 'ts', typescript: 'ts',
        tsv: 'tsv',
        vb: 'vb', vba: 'vba', vbnet: 'vb',
        verilog: 'v', vhdl: 'vhd',
        yaml: 'yaml', yml: 'yml',
        zig: 'zig',
    };
    return map[lang.toLowerCase()] || 'txt';
}

export function downloadCode(code: string, lang: string | undefined) {
    const ext = getExtension(lang);
    const filename = lang?.toLowerCase() === 'dockerfile' ? 'Dockerfile' : `codeblock.${ext}`;
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
