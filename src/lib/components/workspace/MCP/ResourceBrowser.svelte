<script lang="ts">
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { MCPServer, MCPResource } from '$lib/apis/mcp';
	import { listMCPResources, readMCPResource } from '$lib/apis/mcp';

	import Modal from '../../common/Modal.svelte';
	import Spinner from '../../common/Spinner.svelte';
	import Search from '../../icons/Search.svelte';
	import XMark from '../../icons/XMark.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let server: MCPServer;

	let loading = false;
	let resources: MCPResource[] = [];
	let filteredResources: MCPResource[] = [];
	let query = '';

	let selectedResource: MCPResource | null = null;
	let resourceContent: any = null;
	let loadingContent = false;

	$: if (resources && query !== undefined) {
		filteredResources = resources.filter((r) => {
			if (query === '') return true;
			const lowerQuery = query.toLowerCase();
			return (
				(r.name || '').toLowerCase().includes(lowerQuery) ||
				(r.uri || '').toLowerCase().includes(lowerQuery) ||
				(r.description || '').toLowerCase().includes(lowerQuery)
			);
		});
	}

	const loadResources = async (refresh = false) => {
		loading = true;
		try {
			resources = await listMCPResources(localStorage.token, server.id, refresh);
		} catch (error) {
			toast.error($i18n.t('Failed to load resources'));
			console.error(error);
		} finally {
			loading = false;
		}
	};

	const handleResourceClick = async (resource: MCPResource) => {
		selectedResource = resource;
		loadingContent = true;
		resourceContent = null;

		try {
			const result = await readMCPResource(localStorage.token, server.id, resource.uri);
			resourceContent = result;
		} catch (error) {
			toast.error($i18n.t('Failed to read resource'));
			console.error(error);
		} finally {
			loadingContent = false;
		}
	};

	const handleRefresh = async () => {
		await loadResources(true);
		toast.success($i18n.t('Resources refreshed'));
	};

	const closeContentView = () => {
		selectedResource = null;
		resourceContent = null;
	};

	onMount(async () => {
		if (show) {
			await loadResources();
		}
	});

	$: if (show) {
		loadResources();
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
			<!-- Resource List Panel -->
			<div class="w-1/3 border-r border-gray-200 dark:border-gray-700 flex flex-col">
				<!-- Header -->
				<div class="p-4 border-b border-gray-200 dark:border-gray-700">
					<div class="flex items-center justify-between mb-3">
						<h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
							{$i18n.t('Resources')}
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
							placeholder={$i18n.t('Search resources...')}
							class="flex-1 text-sm bg-transparent outline-none"
						/>
						{#if query}
							<button on:click={() => (query = '')}>
								<XMark className="size-3" />
							</button>
						{/if}
					</div>
				</div>

				<!-- Resource List -->
				<div class="flex-1 overflow-y-auto p-2">
					{#if loading}
						<div class="flex justify-center items-center h-32">
							<Spinner className="size-6" />
						</div>
					{:else if filteredResources.length === 0}
						<div class="flex flex-col items-center justify-center h-32 text-center">
							<div class="text-gray-500 dark:text-gray-400 text-sm">
								{query
									? $i18n.t('No resources found matching your search')
									: $i18n.t('No resources available')}
							</div>
						</div>
					{:else}
						<div class="space-y-1">
							{#each filteredResources as resource}
								<button
									class="w-full text-left p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition {selectedResource?.uri ===
									resource.uri
										? 'bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600'
										: ''}"
									on:click={() => handleResourceClick(resource)}
								>
									<div class="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
										{resource.name || resource.uri}
									</div>
									{#if resource.description}
										<div class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
											{resource.description}
										</div>
									{/if}
									{#if resource.mimeType}
										<div class="text-xs text-gray-500 dark:text-gray-500 mt-1">
											{resource.mimeType}
										</div>
									{/if}
								</button>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Content Panel -->
			<div class="flex-1 flex flex-col">
				{#if selectedResource}
					<!-- Content Header -->
					<div class="p-4 border-b border-gray-200 dark:border-gray-700">
						<div class="flex items-start justify-between">
							<div class="flex-1 min-w-0">
								<h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
									{selectedResource.name || selectedResource.uri}
								</h3>
								{#if selectedResource.description}
									<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
										{selectedResource.description}
									</p>
								{/if}
								<div class="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-500">
									<code class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
										{selectedResource.uri}
									</code>
									{#if selectedResource.mimeType}
										<span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
											{selectedResource.mimeType}
										</span>
									{/if}
								</div>
							</div>
							<button
								class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
								on:click={closeContentView}
							>
								<XMark className="size-4" />
							</button>
						</div>
					</div>

					<!-- Content Body -->
					<div class="flex-1 overflow-y-auto p-4">
						{#if loadingContent}
							<div class="flex justify-center items-center h-32">
								<Spinner className="size-6" />
							</div>
						{:else if resourceContent}
							<div class="prose dark:prose-invert max-w-none">
								{#if Array.isArray(resourceContent.contents)}
									{#each resourceContent.contents as content}
										{#if content.type === 'text'}
											<pre class="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto">{content.text}</pre>
										{:else if content.type === 'blob'}
											<div class="text-sm text-gray-600 dark:text-gray-400">
												Binary content ({content.mimeType})
											</div>
										{/if}
									{/each}
								{:else}
									<pre class="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto">{JSON.stringify(
											resourceContent,
											null,
											2
										)}</pre>
								{/if}
							</div>
						{/if}
					</div>
				{:else}
					<!-- Empty State -->
					<div class="flex-1 flex items-center justify-center">
						<div class="text-center text-gray-500 dark:text-gray-400">
							<div class="text-4xl mb-2">📚</div>
							<div class="text-sm">{$i18n.t('Select a resource to view its content')}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</Modal>
{/if}
