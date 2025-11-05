<script lang="ts">
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { MCPServer, MCPTool } from '$lib/apis/mcp';
	import { listMCPTools, callMCPTool } from '$lib/apis/mcp';

	import Modal from '../../common/Modal.svelte';
	import Spinner from '../../common/Spinner.svelte';
	import Search from '../../icons/Search.svelte';
	import XMark from '../../icons/XMark.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let server: MCPServer;

	let loading = false;
	let tools: MCPTool[] = [];
	let filteredTools: MCPTool[] = [];
	let query = '';

	let selectedTool: MCPTool | null = null;
	let toolArgs: Record<string, any> = {};
	let toolResult: any = null;
	let executingTool = false;

	$: if (tools && query !== undefined) {
		filteredTools = tools.filter((t) => {
			if (query === '') return true;
			const lowerQuery = query.toLowerCase();
			return (
				(t.name || '').toLowerCase().includes(lowerQuery) ||
				(t.description || '').toLowerCase().includes(lowerQuery)
			);
		});
	}

	const loadTools = async (refresh = false) => {
		loading = true;
		try {
			tools = await listMCPTools(localStorage.token, server.id, refresh);
		} catch (error) {
			toast.error($i18n.t('Failed to load tools'));
			console.error(error);
		} finally {
			loading = false;
		}
	};

	const handleToolClick = (tool: MCPTool) => {
		selectedTool = tool;
		toolResult = null;

		// Initialize tool args from schema
		toolArgs = {};
		if (tool.inputSchema && tool.inputSchema.properties) {
			Object.keys(tool.inputSchema.properties).forEach((key) => {
				const prop = tool.inputSchema.properties[key];
				if (prop.default !== undefined) {
					toolArgs[key] = prop.default;
				} else if (prop.type === 'string') {
					toolArgs[key] = '';
				} else if (prop.type === 'number' || prop.type === 'integer') {
					toolArgs[key] = 0;
				} else if (prop.type === 'boolean') {
					toolArgs[key] = false;
				} else if (prop.type === 'array') {
					toolArgs[key] = [];
				} else if (prop.type === 'object') {
					toolArgs[key] = {};
				}
			});
		}
	};

	const handleExecuteTool = async () => {
		if (!selectedTool) return;

		executingTool = true;
		toolResult = null;

		try {
			const result = await callMCPTool(localStorage.token, server.id, selectedTool.name, toolArgs);
			toolResult = result;
			toast.success($i18n.t('Tool executed successfully'));
		} catch (error) {
			toast.error($i18n.t('Failed to execute tool'));
			console.error(error);
			toolResult = { error: String(error) };
		} finally {
			executingTool = false;
		}
	};

	const handleRefresh = async () => {
		await loadTools(true);
		toast.success($i18n.t('Tools refreshed'));
	};

	const closeToolView = () => {
		selectedTool = null;
		toolArgs = {};
		toolResult = null;
	};

	const getInputType = (type: string) => {
		switch (type) {
			case 'string':
				return 'text';
			case 'number':
			case 'integer':
				return 'number';
			case 'boolean':
				return 'checkbox';
			default:
				return 'text';
		}
	};

	onMount(async () => {
		if (show) {
			await loadTools();
		}
	});

	$: if (show) {
		loadTools();
	}
</script>

{#if show}
	<Modal
		size="xl"
		on:close={() => {
			show = false;
		}}
	>
		<div class="flex h-[600px]">
			<!-- Tool List Panel -->
			<div class="w-1/3 border-r border-gray-200 dark:border-gray-700 flex flex-col">
				<!-- Header -->
				<div class="p-4 border-b border-gray-200 dark:border-gray-700">
					<div class="flex items-center justify-between mb-3">
						<h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
							{$i18n.t('Tools')}
						</h2>
						<button
							class="px-2 py-1 text-xs rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition"
							on:click={handleRefresh}
							disabled={loading}
						>
							{loading ? $i18n.t('Loading...') : $i18n.t('Refresh')}
						</button>
					</div>

					<!-- Server Info -->
					<div class="text-sm text-gray-600 dark:text-gray-400 mb-3">
						<div class="font-medium truncate">{server.name}</div>
					</div>

					<!-- Search -->
					<div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-850">
						<Search className="size-3.5" />
						<input
							type="text"
							bind:value={query}
							placeholder={$i18n.t('Search tools...')}
							class="flex-1 text-sm bg-transparent outline-none"
						/>
						{#if query}
							<button on:click={() => (query = '')}>
								<XMark className="size-3" />
							</button>
						{/if}
					</div>
				</div>

				<!-- Tool List -->
				<div class="flex-1 overflow-y-auto p-2">
					{#if loading}
						<div class="flex justify-center items-center h-32">
							<Spinner className="size-6" />
						</div>
					{:else if filteredTools.length === 0}
						<div class="flex flex-col items-center justify-center h-32 text-center">
							<div class="text-gray-500 dark:text-gray-400 text-sm">
								{query
									? $i18n.t('No tools found matching your search')
									: $i18n.t('No tools available')}
							</div>
						</div>
					{:else}
						<div class="space-y-1">
							{#each filteredTools as tool}
								<button
									class="w-full text-left p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition {selectedTool?.name ===
									tool.name
										? 'bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600'
										: ''}"
									on:click={() => handleToolClick(tool)}
								>
									<div class="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
										{tool.name}
									</div>
									{#if tool.description}
										<div class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
											{tool.description}
										</div>
									{/if}
								</button>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Tool Detail Panel -->
			<div class="flex-1 flex flex-col">
				{#if selectedTool}
					<!-- Tool Header -->
					<div class="p-4 border-b border-gray-200 dark:border-gray-700">
						<div class="flex items-start justify-between">
							<div class="flex-1 min-w-0">
								<h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
									{selectedTool.name}
								</h3>
								{#if selectedTool.description}
									<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
										{selectedTool.description}
									</p>
								{/if}
							</div>
							<button
								class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
								on:click={closeToolView}
							>
								<XMark className="size-4" />
							</button>
						</div>
					</div>

					<!-- Tool Form & Result -->
					<div class="flex-1 overflow-y-auto p-4 space-y-4">
						<!-- Input Form -->
						<div class="space-y-3">
							<h4 class="font-medium text-sm text-gray-900 dark:text-gray-100">
								{$i18n.t('Parameters')}
							</h4>

							{#if selectedTool.inputSchema && selectedTool.inputSchema.properties}
								{#each Object.entries(selectedTool.inputSchema.properties) as [key, schema]}
									<div>
										<label
											for={key}
											class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
										>
											{schema.title || key}
											{#if selectedTool.inputSchema.required?.includes(key)}
												<span class="text-red-500">*</span>
											{/if}
										</label>

										{#if schema.description}
											<p class="text-xs text-gray-500 dark:text-gray-500 mb-1">
												{schema.description}
											</p>
										{/if}

										{#if schema.type === 'boolean'}
											<input
												id={key}
												type="checkbox"
												bind:checked={toolArgs[key]}
												class="w-4 h-4 rounded border-gray-300 dark:border-gray-700 text-blue-600 focus:ring-blue-500"
											/>
										{:else if schema.type === 'object' || schema.type === 'array'}
											<textarea
												id={key}
												bind:value={toolArgs[key]}
												rows="3"
												class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 font-mono"
												placeholder={schema.type === 'array' ? '[]' : '{}'}
											/>
										{:else}
											<input
												id={key}
												type={getInputType(schema.type)}
												bind:value={toolArgs[key]}
												class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
												placeholder={schema.default !== undefined
													? String(schema.default)
													: ''}
											/>
										{/if}
									</div>
								{/each}
							{:else}
								<div class="text-sm text-gray-500 dark:text-gray-500">
									{$i18n.t('No parameters required')}
								</div>
							{/if}
						</div>

						<!-- Execute Button -->
						<button
							class="w-full px-4 py-2 rounded-lg bg-black text-white dark:bg-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200 transition font-medium flex items-center justify-center gap-2"
							on:click={handleExecuteTool}
							disabled={executingTool}
						>
							{#if executingTool}
								<Spinner className="size-4" />
								<span>{$i18n.t('Executing...')}</span>
							{:else}
								<span>▶️</span>
								<span>{$i18n.t('Execute Tool')}</span>
							{/if}
						</button>

						<!-- Result -->
						{#if toolResult !== null}
							<div class="space-y-2">
								<h4 class="font-medium text-sm text-gray-900 dark:text-gray-100">
									{$i18n.t('Result')}
								</h4>
								<div
									class="p-4 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700"
								>
									{#if toolResult.error}
										<div class="text-red-600 dark:text-red-400 text-sm">
											Error: {toolResult.error}
										</div>
									{:else if Array.isArray(toolResult.content)}
										{#each toolResult.content as content}
											{#if content.type === 'text'}
												<pre class="whitespace-pre-wrap text-sm">{content.text}</pre>
											{:else}
												<pre class="whitespace-pre-wrap text-sm text-gray-600 dark:text-gray-400">{JSON.stringify(
														content,
														null,
														2
													)}</pre>
											{/if}
										{/each}
									{:else}
										<pre class="whitespace-pre-wrap text-sm">{JSON.stringify(
												toolResult,
												null,
												2
											)}</pre>
									{/if}
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<!-- Empty State -->
					<div class="flex-1 flex items-center justify-center">
						<div class="text-center text-gray-500 dark:text-gray-400">
							<div class="text-4xl mb-2">🔧</div>
							<div class="text-sm">{$i18n.t('Select a tool to view details and execute')}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</Modal>
{/if}
