<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	const i18n = getContext('i18n');

	import { WEBUI_NAME, user } from '$lib/stores';
	import { goto } from '$app/navigation';

	import {
		getMCPServers,
		createMCPServer,
		deleteMCPServerById,
		toggleMCPServerById,
		toggleMCPServerGlobalById,
		checkMCPServerHealth,
		generateMCPConfig,
		downloadMCPConfig,
		type MCPServer,
		type MCPServerForm
	} from '$lib/apis/mcp';

	import Search from '../icons/Search.svelte';
	import Plus from '../icons/Plus.svelte';
	import XMark from '../icons/XMark.svelte';
	import Spinner from '../common/Spinner.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import ConfirmDialog from '../common/ConfirmDialog.svelte';

	// Import MCP-specific components (to be created)
	import ServerCard from './MCP/ServerCard.svelte';
	import ServerFormModal from './MCP/ServerFormModal.svelte';
	import ResourceBrowser from './MCP/ResourceBrowser.svelte';
	import ToolBrowser from './MCP/ToolBrowser.svelte';

	let loaded = false;
	let query = '';
	let servers: MCPServer[] = [];
	let filteredServers: MCPServer[] = [];

	let showServerFormModal = false;
	let selectedServer: MCPServer | null = null;
	let formMode: 'create' | 'edit' = 'create';

	let showDeleteConfirm = false;
	let serverToDelete: MCPServer | null = null;

	let showResourceBrowser = false;
	let showToolBrowser = false;
	let browserServer: MCPServer | null = null;

	let healthCheckInProgress: Record<string, boolean> = {};

	// Health status colors
	const getHealthStatusColor = (status?: string) => {
		switch (status) {
			case 'healthy':
				return 'text-green-500';
			case 'unhealthy':
				return 'text-red-500';
			case 'unknown':
			default:
				return 'text-gray-500';
		}
	};

	const getHealthStatusBadge = (status?: string) => {
		switch (status) {
			case 'healthy':
				return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
			case 'unhealthy':
				return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
			case 'unknown':
			default:
				return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400';
		}
	};

	$: if (servers && query !== undefined) {
		setFilteredServers();
	}

	const setFilteredServers = () => {
		filteredServers = servers.filter((s) => {
			if (query === '') return true;
			const lowerQuery = query.toLowerCase();
			return (
				(s.name || '').toLowerCase().includes(lowerQuery) ||
				(s.id || '').toLowerCase().includes(lowerQuery) ||
				(s.type || '').toLowerCase().includes(lowerQuery) ||
				(s.description || '').toLowerCase().includes(lowerQuery)
			);
		});
	};

	const loadServers = async () => {
		try {
			servers = await getMCPServers(localStorage.token);
		} catch (error) {
			toast.error($i18n.t('Failed to load MCP servers'));
			console.error(error);
		}
	};

	const handleCreateServer = () => {
		formMode = 'create';
		selectedServer = null;
		showServerFormModal = true;
	};

	const handleEditServer = (server: MCPServer) => {
		formMode = 'edit';
		selectedServer = server;
		showServerFormModal = true;
	};

	const handleServerFormSubmit = async (serverForm: MCPServerForm) => {
		try {
			if (formMode === 'create') {
				await createMCPServer(localStorage.token, serverForm);
				toast.success($i18n.t('MCP server created successfully'));
			} else if (selectedServer) {
				// Update handled via API
				toast.success($i18n.t('MCP server updated successfully'));
			}
			await loadServers();
			showServerFormModal = false;
			selectedServer = null;
		} catch (error) {
			toast.error($i18n.t('Failed to save MCP server'));
			console.error(error);
		}
	};

	const handleDeleteClick = (server: MCPServer) => {
		serverToDelete = server;
		showDeleteConfirm = true;
	};

	const handleDeleteConfirm = async () => {
		if (serverToDelete) {
			try {
				await deleteMCPServerById(localStorage.token, serverToDelete.id);
				toast.success($i18n.t('MCP server deleted successfully'));
				await loadServers();
			} catch (error) {
				toast.error($i18n.t('Failed to delete MCP server'));
				console.error(error);
			}
		}
		showDeleteConfirm = false;
		serverToDelete = null;
	};

	const handleToggleEnabled = async (server: MCPServer) => {
		try {
			await toggleMCPServerById(localStorage.token, server.id);
			toast.success(
				server.enabled
					? $i18n.t('MCP server disabled')
					: $i18n.t('MCP server enabled')
			);
			await loadServers();
		} catch (error) {
			toast.error($i18n.t('Failed to toggle MCP server'));
			console.error(error);
		}
	};

	const handleToggleGlobal = async (server: MCPServer) => {
		try {
			await toggleMCPServerGlobalById(localStorage.token, server.id);
			toast.success(
				server.is_global
					? $i18n.t('MCP server set to private')
					: $i18n.t('MCP server set to global')
			);
			await loadServers();
		} catch (error) {
			toast.error($i18n.t('Failed to toggle global access'));
			console.error(error);
		}
	};

	const handleHealthCheck = async (server: MCPServer) => {
		healthCheckInProgress[server.id] = true;
		try {
			const result = await checkMCPServerHealth(localStorage.token, server.id);
			toast.success(
				result.status === 'healthy'
					? $i18n.t('Server is healthy')
					: $i18n.t('Server is unhealthy')
			);
			await loadServers();
		} catch (error) {
			toast.error($i18n.t('Health check failed'));
			console.error(error);
		} finally {
			healthCheckInProgress[server.id] = false;
		}
	};

	const handleViewResources = (server: MCPServer) => {
		browserServer = server;
		showResourceBrowser = true;
	};

	const handleViewTools = (server: MCPServer) => {
		browserServer = server;
		showToolBrowser = true;
	};

	const handleDownloadConfig = async (platform: string = 'standard') => {
		try {
			const blob = await downloadMCPConfig(localStorage.token, platform);
			if (blob) {
				const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a');
				a.href = url;
				a.download = `mcp_generated_config.json`;
				document.body.appendChild(a);
				a.click();
				window.URL.revokeObjectURL(url);
				document.body.removeChild(a);
				toast.success($i18n.t('Configuration downloaded'));
			}
		} catch (error) {
			toast.error($i18n.t('Failed to download configuration'));
			console.error(error);
		}
	};

	onMount(async () => {
		await loadServers();
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('MCP Servers')} • {$WEBUI_NAME}
	</title>
</svelte:head>

<ConfirmDialog
	bind:show={showDeleteConfirm}
	on:confirm={handleDeleteConfirm}
	message={$i18n.t('Are you sure you want to delete this MCP server?')}
/>

<ServerFormModal
	bind:show={showServerFormModal}
	bind:server={selectedServer}
	mode={formMode}
	on:submit={(e) => handleServerFormSubmit(e.detail)}
/>

{#if showResourceBrowser && browserServer}
	<ResourceBrowser
		bind:show={showResourceBrowser}
		server={browserServer}
	/>
{/if}

{#if showToolBrowser && browserServer}
	<ToolBrowser
		bind:show={showToolBrowser}
		server={browserServer}
	/>
{/if}

{#if loaded}
	<div class="flex flex-col gap-1 px-1 mt-1.5 mb-3">
		<div class="flex justify-between items-center">
			<div class="flex items-center md:self-center text-xl font-medium px-0.5 gap-2 shrink-0">
				<div>{$i18n.t('MCP Servers')}</div>
				<div class="text-lg font-medium text-gray-500 dark:text-gray-500">
					{filteredServers.length}
				</div>
			</div>

			<div class="flex w-full justify-end gap-1.5">
				<button
					class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-200 transition"
					on:click={() => handleDownloadConfig('standard')}
				>
					<div class="self-center font-medium line-clamp-1">
						{$i18n.t('Export Config')}
					</div>
				</button>

				<button
					class="px-2 py-1.5 rounded-xl bg-black text-white dark:bg-white dark:text-black transition font-medium text-sm flex items-center"
					on:click={handleCreateServer}
				>
					<Plus className="size-3" strokeWidth="2.5" />
					<div class="hidden md:block md:ml-1 text-xs">{$i18n.t('New Server')}</div>
				</button>
			</div>
		</div>
	</div>

	<div class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100 dark:border-gray-850">
		<!-- Search Bar -->
		<div class="flex w-full space-x-2 py-0.5 px-3.5 pb-2">
			<div class="flex flex-1">
				<div class="self-center ml-1 mr-3">
					<Search className="size-3.5" />
				</div>
				<input
					class="w-full text-sm pr-4 py-1 rounded-r-xl outline-hidden bg-transparent"
					bind:value={query}
					placeholder={$i18n.t('Search MCP Servers')}
				/>
				{#if query}
					<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
						<button
							class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
							on:click={() => {
								query = '';
							}}
						>
							<XMark className="size-3" strokeWidth="2" />
						</button>
					</div>
				{/if}
			</div>
		</div>

		<!-- Server List -->
		<div class="px-3 pt-1 pb-2 flex flex-col gap-2">
			{#if filteredServers.length === 0}
				<div class="flex flex-col items-center justify-center py-12 text-center">
					<div class="text-gray-500 dark:text-gray-400 text-sm">
						{query
							? $i18n.t('No MCP servers found matching your search')
							: $i18n.t('No MCP servers configured')}
					</div>
					{#if !query}
						<button
							class="mt-4 px-4 py-2 rounded-xl bg-black text-white dark:bg-white dark:text-black transition font-medium text-sm"
							on:click={handleCreateServer}
						>
							{$i18n.t('Create Your First Server')}
						</button>
					{/if}
				</div>
			{:else}
				{#each filteredServers as server (server.id)}
					<ServerCard
						{server}
						healthChecking={healthCheckInProgress[server.id] || false}
						on:edit={() => handleEditServer(server)}
						on:delete={() => handleDeleteClick(server)}
						on:toggleEnabled={() => handleToggleEnabled(server)}
						on:toggleGlobal={() => handleToggleGlobal(server)}
						on:healthCheck={() => handleHealthCheck(server)}
						on:viewResources={() => handleViewResources(server)}
						on:viewTools={() => handleViewTools(server)}
					/>
				{/each}
			{/if}
		</div>
	</div>
{:else}
	<div class="flex justify-center items-center h-64">
		<Spinner className="size-6" />
	</div>
{/if}
