<script lang="ts">
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	import { executeCode } from '$lib/apis/utils';
	import { config, settings, showArtifacts, showControls } from '$lib/stores';
	import { copyToClipboard, createMessagesList } from '$lib/utils';
	import SvgPanZoom from '../common/SVGPanZoom.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import ArrowLeft from '../icons/ArrowLeft.svelte';
	import ArrowsPointingOut from '../icons/ArrowsPointingOut.svelte';
	import XMark from '../icons/XMark.svelte';

	export let overlay = false;
	export let history;
	let messages: any[] = [];

	let contents: Array<{ type: string; content: string }> = [];
	let selectedContentIdx = 0;

	let copied = false;
	let iframeElement: HTMLIFrameElement;

	let latexArtifacts = [];
	let latexResults: Record<number, string> = {};
	let latexLoading = false;
	let latexError = '';

	// LaTeX risky patterns (copied from CodeBlock.svelte)
	const latexRisky: RegExp[] = [
		/\\write\s*\d*/i,
		/\\write18/i,
		/\\immediate/i,
		/\\input\s*(\{.*?\})?/i,
		/\\@@input/i,
		/\\openout/i,
		/\\openin/i,
		/\\read\s*\d*/i,
		/\\closeout/i,
		/\\closein/i,
		/\\usepackage\s*\{\s*shellesc\s*\}/i,
		/\\usepackage\s*\{\s*catchfile\s*\}/i,
		/\\catcode/i,
		/\\newwrite/i,
		/\\newread/i,
		/\\loop/i,
		/\\everyeof/i,
		/\\everypar/i,
		/\\everymath/i,
		/\\everydisplay/i,
		/\\everycr/i,
		/\\everyjob/i,
		/\\everyhbox/i,
		/\\everyvbox/i,
		/\\everygroup/i,
		/\\everyline/i,
		/\\everyrow/i,
		/\\everysection/i,
		/\\everychapter/i,
		/\\everypage/i,
		/\\everyfootnote/i,
		/\\special/i,
		/\\jobname/i,
		/\\message/i,
		/\\errmessage/i,
		/\\batchmode/i,
		/\\scrollmode/i,
		/\\nonstopmode/i,
		/\\errorstopmode/i,
		/\\chardef/i,
		/\\advance/i,
		/\\multiply/i,
		/\\divide/i,
		/\\endinput/i,
		/\\dump/i
	];

	function isLatexSafe(code: string): boolean {
		return !latexRisky.some((pat) => pat.test(code));
	}

	$: if (history) {
		messages = createMessagesList(history, history.currentId);
		getContents();
	} else {
		messages = [];
		getContents();
	}

	// Helper: Detect LaTeX code blocks or inline LaTeX
	function extractLatex(content: string) {
		const blocks: string[] = [];
		// Detect ```latex or ```tex code blocks
		const codeBlockRegex = /```(?:latex|tex)\n([\s\S]*?)```/gi;
		let match;
		while ((match = codeBlockRegex.exec(content))) {
			blocks.push(match[1]);
		}

		// Detect inline LaTeX: \\documentclass or \\begin{document} ... \\end{document}
		// const inlineLatexRegex = /(\\documentclass[\s\S]*?\\end{document})/gi;
		// while ((match = inlineLatexRegex.exec(content))) {
		// 	blocks.push(match[1]);
		// }

		return blocks;
	}

	const getContents = async () => {
		contents = [];
		latexArtifacts = [];
		latexResults = {};
		latexError = '';
		let foundLatex = false;
		for (const message of messages) {
			if (message?.role !== 'user' && message?.content) {
				const codeBlockContents = message.content.match(/```[\s\S]*?```/g);
				let codeBlocks: { lang: string; code: string }[] = [];

				if (codeBlockContents) {
					codeBlockContents.forEach((block: string) => {
						const lang = block.split('\n')[0].replace('```', '').trim().toLowerCase();
						const code = block.replace(/```[\s\S]*?\n/, '').replace(/```$/, '');
						codeBlocks.push({ lang, code });
					});
				}

				let htmlContent = '';
				let cssContent = '';
				let jsContent = '';

				codeBlocks.forEach((block: { lang: string; code: string }) => {
					const { lang, code } = block;

					if (lang === 'html') {
						htmlContent += code + '\n';
					} else if (lang === 'css') {
						cssContent += code + '\n';
					} else if (lang === 'javascript' || lang === 'js') {
						jsContent += code + '\n';
					} else if (lang === 'latex' || lang === 'tex') {
						// Skip LaTeX/tex blocks here; they will be handled by the LaTeX artifact detection below
						return;
					}
				});

				const inlineHtml = message.content.match(/<html>[\s\S]*?<\/html>/gi);
				const inlineCss = message.content.match(/<style>[\s\S]*?<\/style>/gi);
				const inlineJs = message.content.match(/<script>[\s\S]*?<\/script>/gi);

				if (inlineHtml) {
					inlineHtml.forEach((block: string) => {
						const content = block.replace(/<\/?html>/gi, ''); // Remove <html> tags
						htmlContent += content + '\n';
					});
				}
				if (inlineCss) {
					inlineCss.forEach((block: string) => {
						const content = block.replace(/<\/?style>/gi, ''); // Remove <style> tags
						cssContent += content + '\n';
					});
				}
				if (inlineJs) {
					inlineJs.forEach((block: string) => {
						const content = block.replace(/<\/?script>/gi, ''); // Remove <script> tags
						jsContent += content + '\n';
					});
				}

				if (htmlContent || cssContent || jsContent) {
					const renderedContent = `
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
							<${''}style>
								body {
									background-color: white; /* Ensure the iframe has a white background */
								}

								${cssContent}
							</${''}style>
                        </head>
                        <body>
                            ${htmlContent}

							<${''}script>
                            	${jsContent}
							</${''}script>
                        </body>
                        </html>
                    `;
					contents = [...contents, { type: 'iframe', content: renderedContent }];
				} else {
					// Check for SVG content
					for (const block of codeBlocks) {
						if (block.lang === 'svg' || (block.lang === 'xml' && block.code.includes('<svg'))) {
							contents = [...contents, { type: 'svg', content: block.code }];
						}
					}
				}

				// LaTeX artifact detection (only if Jupyter enabled)
				if ($config?.code?.engine === 'jupyter') {
					const latexBlocks = extractLatex(message.content);
					if (latexBlocks.length > 0) {
						foundLatex = true;
						for (const latexCode of latexBlocks) {
							latexArtifacts.push(latexCode);
							contents = [...contents, { type: 'latex', content: latexCode }];
						}
					}
				}
			}
		}

		if (contents.length === 0) {
			showControls.set(false);
			showArtifacts.set(false);
		}

		selectedContentIdx = contents ? contents.length - 1 : 0;
	};

	// LaTeX PDF generation logic
	async function generateLatexPdf(idx: number) {
		latexLoading = true;
		latexError = '';
		const code = contents[idx].content;
		if (!isLatexSafe(code)) {
			latexError =
				(i18n as any)?.t?.(
					'Code contains potentially dangerous LaTeX operations and was blocked.'
				) || 'Code contains potentially dangerous LaTeX operations and was blocked.';
			latexLoading = false;
			return;
		}
		const filename = `temp_${Date.now()}.tex`;
		const pdffile = filename.replace(/\.tex$/, '.pdf');
		const writefile = `%%writefile ${filename}\n${code}`;
		const compileCmd = `timeout 30s pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape ${filename}`;
		const bashCompile = `%%bash\n${compileCmd}`;
		const base64Cmd = `%%bash\nif [ -f ${pdffile} ]; then base64 ${pdffile}; fi`;
		const cleanupCmd = `%%bash\nrm -f ${filename} ${filename.replace(/\.tex$/, '.aux')} ${filename.replace(/\.tex$/, '.log')} ${pdffile}`;
		try {
			await executeCode(localStorage.token, writefile);
			const compileOutput = await executeCode(localStorage.token, bashCompile);
			if (!compileOutput || compileOutput.stderr) {
				latexError =
					(i18n as any)?.t?.('LaTeX document failed to compile.') ||
					'LaTeX document failed to compile.';
				await executeCode(localStorage.token, cleanupCmd).catch(() => {});
				latexLoading = false;
				return;
			}
			const base64Output = await executeCode(localStorage.token, base64Cmd);
			await executeCode(localStorage.token, cleanupCmd).catch(() => {});
			if (base64Output && base64Output.stdout) {
				latexResults[idx] = `data:application/pdf;base64,${base64Output.stdout.replace(/\s/g, '')}`;
			} else {
				latexError = 'PDF generation failed';
			}
		} catch (e) {
			if (e instanceof Error) {
				latexError = e.message || 'LaTeX execution failed';
			} else {
				latexError = 'LaTeX execution failed';
			}
		} finally {
			latexLoading = false;
		}
	}

	// Watch for LaTeX artifact selection and auto-generate PDF
	$: if (
		contents[selectedContentIdx]?.type === 'latex' &&
		!latexResults[selectedContentIdx] &&
		!latexLoading &&
		!latexError &&
		$config?.code?.engine === 'jupyter'
	) {
		generateLatexPdf(selectedContentIdx);
	}

	function navigateContent(direction: 'prev' | 'next') {
		console.log(selectedContentIdx);

		selectedContentIdx =
			direction === 'prev'
				? Math.max(selectedContentIdx - 1, 0)
				: Math.min(selectedContentIdx + 1, contents.length - 1);

		console.log(selectedContentIdx);
	}

	const iframeLoadHandler = () => {
		iframeElement.contentWindow.addEventListener(
			'click',
			function (e) {
				const target = e.target.closest('a');
				if (target && target.href) {
					e.preventDefault();
					const url = new URL(target.href, iframeElement.baseURI);
					if (url.origin === window.location.origin) {
						iframeElement.contentWindow.history.pushState(
							null,
							'',
							url.pathname + url.search + url.hash
						);
					} else {
						console.log('External navigation blocked:', url.href);
					}
				}
			},
			true
		);

		// Cancel drag when hovering over iframe
		iframeElement.contentWindow.addEventListener('mouseenter', function (e) {
			e.preventDefault();
			iframeElement.contentWindow.addEventListener('dragstart', (event) => {
				event.preventDefault();
			});
		});
	};

	const showFullScreen = () => {
		if (iframeElement.requestFullscreen) {
			iframeElement.requestFullscreen();
		} else if (iframeElement.webkitRequestFullscreen) {
			iframeElement.webkitRequestFullscreen();
		} else if (iframeElement.msRequestFullscreen) {
			iframeElement.msRequestFullscreen();
		}
	};

	onMount(() => {});
</script>

<div class=" w-full h-full relative flex flex-col bg-gray-50 dark:bg-gray-850">
	<div class="w-full h-full flex flex-col flex-1 relative">
		{#if contents.length > 0}
			<div
				class="pointer-events-auto z-20 flex justify-between items-center p-2.5 font-primar text-gray-900 dark:text-white"
			>
				<button
					class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
					on:click={() => {
						showArtifacts.set(false);
					}}
				>
					<ArrowLeft className="size-3.5  text-gray-900 dark:text-white" />
				</button>

				<div class="flex-1 flex items-center justify-between">
					<div class="flex items-center space-x-2">
						<div class="flex items-center gap-0.5 self-center min-w-fit" dir="ltr">
							<button
								class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition disabled:cursor-not-allowed"
								on:click={() => navigateContent('prev')}
								disabled={contents.length <= 1}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2.5"
									class="size-3.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M15.75 19.5 8.25 12l7.5-7.5"
									/>
								</svg>
							</button>

							<div class="text-xs self-center dark:text-gray-100 min-w-fit">
								{$i18n.t('Version {{selectedVersion}} of {{totalVersions}}', {
									selectedVersion: selectedContentIdx + 1,
									totalVersions: contents.length
								})}
							</div>

							<button
								class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition disabled:cursor-not-allowed"
								on:click={() => navigateContent('next')}
								disabled={contents.length <= 1}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2.5"
									class="size-3.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="m8.25 4.5 7.5 7.5-7.5 7.5"
									/>
								</svg>
							</button>
						</div>
					</div>

					<div class="flex items-center gap-1">
						<button
							class="copy-code-button bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
							on:click={() => {
								copyToClipboard(contents[selectedContentIdx].content);
								copied = true;

								setTimeout(() => {
									copied = false;
								}, 2000);
							}}>{copied ? $i18n.t('Copied') : $i18n.t('Copy')}</button
						>

						{#if contents[selectedContentIdx].type === 'iframe'}
							<Tooltip content={$i18n.t('Open in full screen')}>
								<button
									class=" bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md p-0.5"
									on:click={showFullScreen}
								>
									<ArrowsPointingOut className="size-3.5" />
								</button>
							</Tooltip>
						{/if}
					</div>
				</div>

				<button
					class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
					on:click={() => {
						dispatch('close');
						showControls.set(false);
						showArtifacts.set(false);
					}}
				>
					<XMark className="size-3.5 text-gray-900 dark:text-white" />
				</button>
			</div>
		{/if}

		{#if overlay}
			<div class=" absolute top-0 left-0 right-0 bottom-0 z-10"></div>
		{/if}

		<div class="flex-1 w-full h-full">
			<div class=" h-full flex flex-col">
				{#if contents.length > 0}
					<div class="max-w-full w-full h-full">
						{#if contents[selectedContentIdx].type === 'iframe'}
							<iframe
								bind:this={iframeElement}
								title="Content"
								srcdoc={contents[selectedContentIdx].content}
								class="w-full border-0 h-full rounded-none"
								sandbox="allow-scripts{($settings?.iframeSandboxAllowForms ?? false)
									? ' allow-forms'
									: ''}{($settings?.iframeSandboxAllowSameOrigin ?? false)
									? ' allow-same-origin'
									: ''}"
								on:load={iframeLoadHandler}
							></iframe>
						{:else if contents[selectedContentIdx].type === 'svg'}
							<SvgPanZoom
								className=" w-full h-full max-h-full overflow-hidden"
								svg={contents[selectedContentIdx].content}
							/>
						{:else if contents[selectedContentIdx].type === 'latex'}
							{#if latexLoading}
								<div class="flex items-center justify-center h-full">
									{$i18n.t('Generating PDF...')}
								</div>
							{:else if latexError}
								<div class="text-red-500 p-4">{latexError}</div>
							{:else if latexResults[selectedContentIdx]}
								<iframe
									title="Content"
									src={latexResults[selectedContentIdx]}
									class="w-full border-0 h-full rounded-none"
									sandbox="allow-scripts{($settings?.iframeSandboxAllowForms ?? false)
										? ' allow-forms'
										: ''}{($settings?.iframeSandboxAllowSameOrigin ?? false)
										? ' allow-same-origin'
										: ''}"
								></iframe>
							{:else}
								<div class="flex items-center justify-center h-full">
									{$i18n.t('Waiting for PDF...')}
								</div>
							{/if}
						{/if}
					</div>
				{:else}
					<div class="m-auto font-medium text-xs text-gray-900 dark:text-white">
						{$i18n.t('No HTML, CSS, JavaScript, or LaTeX content found.')}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
