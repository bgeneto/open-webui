<script lang="ts">
	import mermaid from 'mermaid';

	import { v4 as uuidv4 } from 'uuid';

	import { copyToClipboard } from '$lib/utils';
	import { downloadCode } from '$lib/utils/download';
	import { getContext, onDestroy, onMount, tick } from 'svelte';

	import 'highlight.js/styles/github-dark.min.css';

	import { executeCode } from '$lib/apis/utils';
	import CodeEditor from '$lib/components/common/CodeEditor.svelte';
	import SvgPanZoom from '$lib/components/common/SVGPanZoom.svelte';
	import ChevronUpDown from '$lib/components/icons/ChevronUpDown.svelte';
	import CommandLine from '$lib/components/icons/CommandLine.svelte';
	import { config } from '$lib/stores';
	import PyodideWorker from '$lib/workers/pyodide.worker?worker';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	export let id = '';

	export let onSave = (e) => {};
	export let onCode = (e) => {};

	export let save = false;
	export let run = true;
	export let collapsed = false;

	export let token;
	export let lang = '';
	export let code = '';
	export let attributes = {};

	export let className = 'my-2';
	export let editorClassName = '';
	export let stickyButtonsClassName = 'top-8';

	let pyodideWorker = null;

	let _code = '';
	$: if (code) {
		updateCode();
	}

	const updateCode = () => {
		_code = code;
	};

	let _token = null;

	let mermaidHtml = null;

	let highlightedCode = null;
	let executing = false;

	let stdout = null;
	let stderr = null;
	let result = null;
	let files = null;

	let copied = false;
	let saved = false;
	let downloaded = false;

	// Utility: Clean up noisy Jupyter/traceback/ANSI output
	function cleanOutput(output: string): string {
		if (!output) return '';
		// Remove ANSI color codes
		output = output.replace(/\u001b\[[0-9;]*m/g, '');
		// Remove Jupyter cell magic lines
		output = output.replace(/^%%.*$/gm, '');
		// Remove IPython traceback headers/footers
		output = output.replace(/-{5,}.*?-{5,}/gs, '');
		// Remove 'Cell In[1]' and similar
		output = output.replace(/^Cell\s+In\[\d+\].*$/gm, '');
		// Remove get_ipython/run_cell_magic lines
		output = output.replace(/get_ipython\(.*run_cell_magic.*\);?/g, '');
		// Remove empty lines at start/end
		output = output.replace(/^[\s\r\n]+|[\s\r\n]+$/g, '');
		output = output.replace(/^---->\s+[0-9]+\s+$/g, '');
		return output;
	}

	const collapseCodeBlock = () => {
		collapsed = !collapsed;
	};

	const saveCode = () => {
		saved = true;

		code = _code;
		onSave(code);

		setTimeout(() => {
			saved = false;
		}, 1000);
	};

	const copyCode = async () => {
		copied = true;
		await copyToClipboard(code);

		setTimeout(() => {
			copied = false;
		}, 1000);
	};

	const checkPythonCode = (str) => {
		// Check if the string contains typical Python syntax characters
		const pythonSyntax = [
			'def ',
			'else:',
			'elif ',
			'try:',
			'except:',
			'finally:',
			'yield ',
			'lambda ',
			'assert ',
			'nonlocal ',
			'del ',
			'True',
			'False',
			'None',
			' and ',
			' or ',
			' not ',
			' in ',
			' is ',
			' with '
		];

		for (let syntax of pythonSyntax) {
			if (str.includes(syntax)) {
				return true;
			}
		}

		// If none of the above conditions met, it's probably not Python code
		return false;
	};

	const checkCppCode = (str) => {
		// C++-exclusive keywords and headers
		const cppSyntax = [
			'std::',
			'cout',
			'cin',
			'class ',
			'template',
			'namespace ',
			'new ',
			'delete ',
			'public:',
			'private:',
			'protected:',
			'using namespace std',
			'operator',
			'friend',
			'virtual',
			'override',
			'nullptr',
			'#include <iostream>',
			'#include <vector>',
			'#include <string>'
		];
		return cppSyntax.some((s) => str.includes(s));
	};

	const checkCCode = (str) => {
		// C-specific keywords/headers, but not C++-exclusive
		if (checkCppCode(str)) return false;
		const cSyntax = [
			'#include <stdio.h>',
			'#include <stdlib.h>',
			'#include <string.h>',
			'printf',
			'scanf',
			'malloc',
			'free',
			'NULL',
			'size_t',
			'struct ',
			'typedef '
		];
		return cSyntax.some((s) => str.includes(s));
	};

	const checkFortranCode = (str) => {
		const fortranSyntax = [
			'program ',
			'end program',
			'implicit none',
			'real',
			'integer',
			'write',
			'print *',
			'subroutine ',
			'function ',
			'module ',
			'end module',
			'contains',
			'allocate'
		];
		return fortranSyntax.some((s) => str.toLowerCase().includes(s));
	};

	const checkLuaCode = (str) => {
		const luaSyntax = [
			'function ',
			'local ',
			'end',
			'then',
			'elseif',
			'repeat',
			'until',
			'require',
			'pairs',
			'ipairs',
			'print(',
			'--',
			'nil',
			'table.',
			'math.',
			'os.',
			'io.'
		];
		return luaSyntax.some((s) => str.includes(s));
	};

	const checkPhpCode = (str) => {
		const phpSyntax = [
			'<?php',
			'echo ',
			'$',
			'->',
			'::',
			'function ',
			'public ',
			'private ',
			'protected ',
			'use ',
			'namespace ',
			'require_once',
			'include_once',
			'array(',
			'null',
			'true',
			'false'
		];
		return phpSyntax.some((s) => str.includes(s));
	};

	function isCodeSafe(code, lang) {
		const riskyPatterns = [
			/\bsystem\s*\(/i,
			/\bpopen\s*\(/i,
			/\bexec/i,
			/\bfork\s*\(/i,
			/\bspawn/i,
			/\bCreateProcess/i,
			/\bWinExec/i,
			/\bShellExecute/i,
			/\bdlopen\s*\(/i,
			/\bLoadLibrary/i,
			/\bSetWindowsHook/i,
			/\bptrace/i,
			/\bkill\s*\(/i,
			/\bsignal\s*\(/i,
			/\batexit\s*\(/i,
			/\bexit\s*\(/i,
			/\babort\s*\(/i,
			/\bremove\s*\(/i,
			/\bunlink\s*\(/i,
			/\brename\s*\(/i,
			/#include\s*<windows\.h>/i,
			/#include\s*<unistd\.h>/i,
			/#include\s*<dlfcn\.h>/i,
			/#include\s*<sys\/types\.h>/i,
			/#include\s*<sys\/wait\.h>/i,
			/#include\s*<sys\/ptrace\.h>/i,
			/#include\s*<process\.h>/i
		];
		const fortranRisky = [
			/\bcall\s+system\b/i,
			/\bexecute_command_line\b/i,
			/\binquire\b/i,
			/\bflush\b/i,
			/\bget_environment_variable\b/i
		];
		const luaRisky = [
			/require\s*\(/i,
			/os\.execute/i,
			/io\.popen/i,
			/os\.remove/i,
			/os\.rename/i,
			/os\.exit/i,
			/os\.setlocale/i,
			/os\.getenv/i,
			/os\.tmpname/i
		];
		const phpRisky = [
			/\bsystem\s*\(/i,
			/\bexec\s*\(/i,
			/\bpopen\s*\(/i,
			/\bshell_exec\s*\(/i,
			/\bpassthru\s*\(/i,
			/\bproc_open\s*\(/i,
			/\bpcntl_exec\s*\(/i,
			/\bpcntl_fork\s*\(/i,
			/\bdelete\s*\(/i,
			/\bunlink\s*\(/i,
			/\bmove_uploaded_file\s*\(/i,
			/\bcopy\s*\(/i,
			/\bchmod\s*\(/i,
			/\bchown\s*\(/i,
			/\bchgrp\s*\(/i
		];
		let patterns = riskyPatterns;
		if (['fortran', 'lua', 'php'].includes(lang?.toLowerCase?.())) {
			if (lang.toLowerCase() === 'fortran') patterns = fortranRisky;
			if (lang.toLowerCase() === 'lua') patterns = luaRisky;
			if (lang.toLowerCase() === 'php') patterns = phpRisky;
		}
		return !patterns.some((pat) => pat.test(code));
	}

	const executePython = async (code) => {
		result = null;
		stdout = null;
		stderr = null;

		executing = true;

		if ($config?.code?.engine === 'jupyter') {
			const output = await executeCode(localStorage.token, code).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			if (output) {
				if (output['stdout']) {
					stdout = output['stdout'];
					const stdoutLines = stdout.split('\n');

					for (const [idx, line] of stdoutLines.entries()) {
						if (line.startsWith('data:image/png;base64')) {
							if (files) {
								files.push({
									type: 'image/png',
									data: line
								});
							} else {
								files = [
									{
										type: 'image/png',
										data: line
									}
								];
							}

							if (stdout.startsWith(`${line}\n`)) {
								stdout = stdout.replace(`${line}\n`, ``);
							} else if (stdout.startsWith(`${line}`)) {
								stdout = stdout.replace(`${line}`, ``);
							}
						}
					}
				}

				if (output['result']) {
					result = output['result'];
					const resultLines = result.split('\n');

					for (const [idx, line] of resultLines.entries()) {
						if (line.startsWith('data:image/png;base64')) {
							if (files) {
								files.push({
									type: 'image/png',
									data: line
								});
							} else {
								files = [
									{
										type: 'image/png',
										data: line
									}
								];
							}

							if (result.startsWith(`${line}\n`)) {
								result = result.replace(`${line}\n`, ``);
							} else if (result.startsWith(`${line}`)) {
								result = result.replace(`${line}`, ``);
							}
						}
					}
				}

				output['stderr'] && (stderr = output['stderr']);
			}

			executing = false;
		} else {
			executePythonAsWorker(code);
		}
	};

	const executePythonAsWorker = async (code) => {
		let packages = [
			code.includes('requests') ? 'requests' : null,
			code.includes('bs4') ? 'beautifulsoup4' : null,
			code.includes('numpy') ? 'numpy' : null,
			code.includes('pandas') ? 'pandas' : null,
			code.includes('sklearn') ? 'scikit-learn' : null,
			code.includes('scipy') ? 'scipy' : null,
			code.includes('re') ? 'regex' : null,
			code.includes('seaborn') ? 'seaborn' : null,
			code.includes('sympy') ? 'sympy' : null,
			code.includes('tiktoken') ? 'tiktoken' : null,
			code.includes('matplotlib') ? 'matplotlib' : null,
			code.includes('pytz') ? 'pytz' : null
		].filter(Boolean);

		console.log(packages);

		pyodideWorker = new PyodideWorker();

		pyodideWorker.postMessage({
			id: id,
			code: code,
			packages: packages
		});

		setTimeout(() => {
			if (executing) {
				executing = false;
				stderr = 'Execution Time Limit Exceeded';
				pyodideWorker.terminate();
			}
		}, 60000);

		pyodideWorker.onmessage = (event) => {
			console.log('pyodideWorker.onmessage', event);
			const { id, ...data } = event.data;

			console.log(id, data);

			if (data['stdout']) {
				stdout = data['stdout'];
				const stdoutLines = stdout.split('\n');

				for (const [idx, line] of stdoutLines.entries()) {
					if (line.startsWith('data:image/png;base64')) {
						if (files) {
							files.push({
								type: 'image/png',
								data: line
							});
						} else {
							files = [
								{
									type: 'image/png',
									data: line
								}
							];
						}

						if (stdout.startsWith(`${line}\n`)) {
							stdout = stdout.replace(`${line}\n`, ``);
						} else if (stdout.startsWith(`${line}`)) {
							stdout = stdout.replace(`${line}`, ``);
						}
					}
				}
			}

			if (data['result']) {
				result = data['result'];
				const resultLines = result.split('\n');

				for (const [idx, line] of resultLines.entries()) {
					if (line.startsWith('data:image/png;base64')) {
						if (files) {
							files.push({
								type: 'image/png',
								data: line
							});
						} else {
							files = [
								{
									type: 'image/png',
									data: line
								}
							];
						}

						if (result.startsWith(`${line}\n`)) {
							result = result.replace(`${line}\n`, ``);
						} else if (result.startsWith(`${line}`)) {
							result = result.replace(`${line}`, ``);
						}
					}
				}
			}

			data['stderr'] && (stderr = data['stderr']);
			data['result'] && (result = data['result']);

			executing = false;
		};

		pyodideWorker.onerror = (event) => {
			console.log('pyodideWorker.onerror', event);
			executing = false;
		};
	};

	const executeJupyterCompiled = async (lang, code) => {
		result = null;
		stdout = null;
		stderr = null;
		executing = true;

		// check if compiled language is supported
		if (!['c', 'cpp', 'fortran'].includes(lang)) {
			toast.error('Currently only C, C++, and Fortran are supported for compiled execution.');
			executing = false;
			return;
		}

		if (!$config?.code?.engine || $config?.code?.engine !== 'jupyter') {
			toast.error('Jupyter engine is required for C/C++/Fortran execution.');
			executing = false;
			return;
		}

		if (!isCodeSafe(code, lang)) {
			toast.error('Code contains potentially dangerous operations and was blocked.');
			executing = false;
			return;
		}

		const ext = lang === 'c' ? 'c' : lang === 'cpp' ? 'cpp' : 'f90';
		const filename = `temp_${uuidv4()}.${ext}`;
		const writefile = `%%writefile ${filename}\n${code}`;
		let compileCmd = '';
		let compilerOptions = '-O2 -lm -fopenmp';
		if (lang === 'c') compileCmd = `gcc ${compilerOptions} ${filename}`;
		if (lang === 'cpp') compileCmd = `g++ ${compilerOptions} ${filename}`;
		if (lang === 'fortran') compileCmd = `gfortran ${compilerOptions} ${filename}`;
		const bash = `%%bash\n${compileCmd}\ntimeout 59s ./a.out`;

		// Write file
		const writeOutput = await executeCode(localStorage.token, writefile).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (!writeOutput) {
			executing = false;
			return;
		}

		// Compile and run
		const output = await executeCode(localStorage.token, bash).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (output) {
			if (output['stdout']) stdout = output['stdout'];
			if (output['stderr']) stderr = output['stderr'];
			if (output['result']) result = output['result'];
		}

		// Cleanup: delete the source file and a.out
		const cleanupCmd = `%%bash\nrm -f ${filename} a.out`;
		await executeCode(localStorage.token, cleanupCmd).catch(() => {});

		executing = false;
	};

	const executeJupyterScript = async (lang, code) => {
		result = null;
		stdout = null;
		stderr = null;
		executing = true;

		// check if script language is supported
		if (!['php', 'lua'].includes(lang)) {
			toast.error('Currently only PHP and Lua are supported for script execution.');
			executing = false;
			return;
		}

		if (!$config?.code?.engine || $config?.code?.engine !== 'jupyter') {
			toast.error('Jupyter engine is required for script execution.');
			executing = false;
			return;
		}

		if (!isCodeSafe(code, lang)) {
			toast.error('Code contains potentially dangerous operations and was blocked.');
			executing = false;
			return;
		}

		const ext = lang === 'php' ? 'php' : lang === 'lua' ? 'lua' : 'txt';
		const filename = `temp_${uuidv4()}.${ext}`;
		const writefile = `%%writefile ${filename}\n${code}`;
		let runCmd = '';
		if (lang === 'php') runCmd = `php ${filename}`;
		if (lang === 'lua') runCmd = `lua ${filename}`;
		const bash = `%%bash\ntimeout 59s ${runCmd}`;

		// Write file
		const writeOutput = await executeCode(localStorage.token, writefile).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (!writeOutput) {
			executing = false;
			return;
		}

		// Run script (with timeout)
		let timeoutId;
		let timedOut = false;
		const timeoutPromise = new Promise((_, reject) => {
			timeoutId = setTimeout(() => {
				timedOut = true;
				reject(new Error('Execution Time Limit Exceeded'));
			}, 60000);
		});

		try {
			const output = await Promise.race([executeCode(localStorage.token, bash), timeoutPromise]);
			if (timedOut) {
				stderr = 'Execution Time Limit Exceeded';
			} else if (output) {
				if (output['stdout']) stdout = output['stdout'];
				if (output['stderr']) stderr = output['stderr'];
				if (output['result']) result = output['result'];
			}
		} catch (e) {
			stderr = e.message || 'Execution failed';
		} finally {
			clearTimeout(timeoutId);
			// Cleanup: delete the source file
			const cleanupCmd = `%%bash\nrm -f ${filename}`;
			await executeCode(localStorage.token, cleanupCmd).catch(() => {});
			executing = false;
		}
	};

	let debounceTimeout;

	const drawMermaidDiagram = async () => {
		try {
			if (await mermaid.parse(code)) {
				const { svg } = await mermaid.render(`mermaid-${uuidv4()}`, code);
				mermaidHtml = svg;
			}
		} catch (error) {
			console.log('Error:', error);
		}
	};

	const render = async () => {
		if (lang === 'mermaid' && (token?.raw ?? '').slice(-4).includes('```')) {
			(async () => {
				await drawMermaidDiagram();
			})();
		}
	};

	$: if (token) {
		if (JSON.stringify(token) !== JSON.stringify(_token)) {
			_token = token;
		}
	}

	$: if (_token) {
		render();
	}

	$: onCode({ lang, code });

	$: if (attributes) {
		onAttributesUpdate();
	}

	const onAttributesUpdate = () => {
		if (attributes?.output) {
			// Create a helper function to unescape HTML entities
			const unescapeHtml = (html) => {
				const textArea = document.createElement('textarea');
				textArea.innerHTML = html;
				return textArea.value;
			};

			try {
				// Unescape the HTML-encoded string
				const unescapedOutput = unescapeHtml(attributes.output);

				// Parse the unescaped string into JSON
				const output = JSON.parse(unescapedOutput);

				// Assign the parsed values to variables
				stdout = output.stdout;
				stderr = output.stderr;
				result = output.result;
			} catch (error) {
				console.error('Error:', error);
			}
		}
	};

	onMount(async () => {
		console.log('codeblock', lang, code);

		if (lang) {
			onCode({ lang, code });
		}
		if (document.documentElement.classList.contains('dark')) {
			mermaid.initialize({
				startOnLoad: true,
				theme: 'dark',
				securityLevel: 'loose'
			});
		} else {
			mermaid.initialize({
				startOnLoad: true,
				theme: 'default',
				securityLevel: 'loose'
			});
		}
	});

	onDestroy(() => {
		if (pyodideWorker) {
			pyodideWorker.terminate();
		}
	});
</script>

<div>
	<div class="relative {className} flex flex-col rounded-lg" dir="ltr">
		{#if lang === 'mermaid'}
			{#if mermaidHtml}
				<SvgPanZoom
					className=" border border-gray-100 dark:border-gray-850 rounded-lg max-h-fit overflow-hidden"
					svg={mermaidHtml}
					content={_token.text}
				/>
			{:else}
				<pre class="mermaid">{code}</pre>
			{/if}
		{:else}
			<div class="text-text-300 absolute pl-4 py-1.5 text-xs font-medium dark:text-white">
				{lang}
			</div>

			<div
				class="sticky {stickyButtonsClassName} mb-1 py-1 pr-2.5 flex items-center justify-end z-10 text-xs text-black dark:text-white"
			>
				<div class="flex items-center gap-0.5 translate-y-[1px]">
					<button
						class="flex gap-1 items-center bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
						on:click={collapseCodeBlock}
					>
						<div>
							<ChevronUpDown className="size-3" />
						</div>

						<div>
							{collapsed ? $i18n.t('Expand') : $i18n.t('Collapse')}
						</div>
					</button>

					{#if ($config?.features?.enable_code_execution ?? true) && (lang.toLowerCase() === 'python' || lang.toLowerCase() === 'py' || (lang === '' && checkPythonCode(code)) || lang.toLowerCase() === 'c' || lang.toLowerCase() === 'cpp' || lang.toLowerCase() === 'fortran' || (lang === '' && (checkCCode(code) || checkCppCode(code) || checkFortranCode(code))) || lang.toLowerCase() === 'lua' || (lang === '' && checkLuaCode(code)) || lang.toLowerCase() === 'php' || (lang === '' && checkPhpCode(code)))}
						{#if executing}
							<div class="run-code-button bg-none border-none p-1 cursor-not-allowed">
								{$i18n.t('Running')}
							</div>
						{:else if run}
							<button
								class="flex gap-1 items-center run-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
								on:click={async () => {
									code = _code;
									await tick();
									if (
										lang.toLowerCase() === 'python' ||
										lang.toLowerCase() === 'py' ||
										(lang === '' && checkPythonCode(code))
									) {
										executePython(code);
									} else if (
										lang.toLowerCase() === 'c' ||
										lang.toLowerCase() === 'cpp' ||
										lang.toLowerCase() === 'fortran' ||
										(lang === '' &&
											(checkCCode(code) || checkCppCode(code) || checkFortranCode(code)))
									) {
										let detectedLang = lang.toLowerCase();
										if (lang === '') {
											if (checkCppCode(code)) detectedLang = 'cpp';
											else if (checkCCode(code)) detectedLang = 'c';
											else if (checkFortranCode(code)) detectedLang = 'fortran';
										}
										executeJupyterCompiled(detectedLang, code);
									} else if (lang.toLowerCase() === 'lua' || (lang === '' && checkLuaCode(code))) {
										if (!isCodeSafe(code, 'lua')) {
											toast.error(
												'Code contains potentially dangerous operations and was blocked.'
											);
											return;
										}
										executeJupyterScript('lua', code);
									} else if (lang.toLowerCase() === 'php' || (lang === '' && checkPhpCode(code))) {
										if (!isCodeSafe(code, 'php')) {
											toast.error(
												'Code contains potentially dangerous operations and was blocked.'
											);
											return;
										}
										executeJupyterScript('php', code);
									}
								}}
							>
								<CommandLine className="size-3" />
								<span>{$i18n.t('Run')}</span>
							</button>
						{/if}
					{/if}

					{#if save}
						<button
							class="save-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
							on:click={saveCode}
						>
							{saved ? $i18n.t('Saved') : $i18n.t('Save')}
						</button>
					{/if}

					<button
						class="copy-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
						on:click={copyCode}>{copied ? $i18n.t('Copied') : $i18n.t('Copy')}</button
					>

					<button
						class="download-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
						on:click={() => {
							downloadCode(code, lang);
							downloaded = true;
							setTimeout(() => (downloaded = false), 1000);
						}}
					>
						{downloaded ? $i18n.t('Downloaded') : '↓ ' + $i18n.t('Download')}
					</button>
				</div>
			</div>

			<div
				class="language-{lang} rounded-t-lg -mt-8 {editorClassName
					? editorClassName
					: executing || stdout || stderr || result
						? ''
						: 'rounded-b-lg'} overflow-hidden"
			>
				<div class=" pt-7 bg-gray-50 dark:bg-gray-850"></div>

				{#if !collapsed}
					<CodeEditor
						value={code}
						{id}
						{lang}
						onSave={() => {
							saveCode();
						}}
						onChange={(value) => {
							_code = value;
						}}
					/>
				{:else}
					<div
						class="bg-gray-50 dark:bg-black dark:text-white rounded-b-lg! pt-2 pb-2 px-4 flex flex-col gap-2 text-xs"
					>
						<span class="text-gray-500 italic">
							{$i18n.t('{{COUNT}} hidden lines', {
								COUNT: code.split('\n').length
							})}
						</span>
					</div>
				{/if}
			</div>

			{#if !collapsed}
				<div
					id="plt-canvas-{id}"
					class="bg-gray-50 dark:bg-[#202123] dark:text-white max-w-full overflow-x-auto scrollbar-hidden"
				/>

				{#if executing || stdout || stderr || result || files}
					<div
						class="bg-gray-50 dark:bg-[#202123] dark:text-white rounded-b-lg! py-4 px-4 flex flex-col gap-2"
					>
						{#if executing}
							<div class=" ">
								<div class=" text-gray-500 text-xs mb-1">STDOUT/STDERR</div>
								<div class="text-sm">Running...</div>
							</div>
						{:else}
							{#if cleanOutput(stderr)}
								<div class=" ">
									<div class=" text-gray-500 text-xs mb-1">STDOUT/STDERR</div>
									<div
										class="text-sm {cleanOutput(stderr)?.split('\n')?.length > 100
											? `max-h-96`
											: ''}  overflow-y-auto"
									>
										{@html cleanOutput(stderr)}
									</div>
								</div>
								{@html `<script>setTimeout(() => {window?.toast?.error?.('${cleanOutput(stderr).split('\\n')[0] || 'Error occurred'}')}, 0)</script>`}
							{:else if stdout}
								<div class=" ">
									<div class=" text-gray-500 text-xs mb-1">STDOUT/STDERR</div>
									<div
										class="text-sm {stdout?.split('\n')?.length > 100
											? `max-h-96`
											: ''}  overflow-y-auto"
									>
										{@html stdout}
									</div>
								</div>
							{/if}
							{#if result || files}
								<div class=" ">
									<div class=" text-gray-500 text-xs mb-1">RESULT</div>
									{#if result}
										<div class="text-sm">{result}</div>
									{/if}
									{#if files}
										<div class="flex flex-col gap-2">
											{#each files as file}
												{#if file.type.startsWith('image')}
													<img src={file.data} alt="Output" class=" w-full max-w-[36rem]" />
												{/if}
											{/each}
										</div>
									{/if}
								</div>
							{/if}
						{/if}
					</div>
				{/if}
			{/if}
		{/if}
	</div>
</div>
