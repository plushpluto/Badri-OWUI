<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { MCPServer } from '$lib/apis/mcp';
	import { user } from '$lib/stores';

	import Tooltip from '../../common/Tooltip.svelte';
	import Spinner from '../../common/Spinner.svelte';
	import EllipsisHorizontal from '../../icons/EllipsisHorizontal.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let server: MCPServer;
	export let healthChecking: boolean = false;

	let showMenu = false;

	const getHealthStatusColor = (status?: string) => {
		switch (status) {
			case 'healthy':
				return 'bg-green-500';
			case 'unhealthy':
				return 'bg-red-500';
			case 'unknown':
			default:
				return 'bg-gray-400';
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

	const getTypeIcon = (type: string) => {
		switch (type) {
			case 'stdio':
				return '🔧'; // Command line
			case 'sse':
				return '📡'; // Server-sent events
			case 'streamable_http':
				return '🌐'; // HTTP
			default:
				return '📦';
		}
	};

	const formatTimestamp = (timestamp?: number) => {
		if (!timestamp) return 'Never';
		const date = new Date(timestamp * 1000);
		const now = Date.now();
		const diff = now - date.getTime();

		// Less than 1 minute
		if (diff < 60000) return 'Just now';
		// Less than 1 hour
		if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
		// Less than 1 day
		if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
		// Less than 7 days
		if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
		// Format as date
		return date.toLocaleDateString();
	};

	const isOwner = $user?.id === server.user_id;
	const canEdit = isOwner || $user?.role === 'admin';
</script>

<div
	class="group relative flex flex-col gap-2 p-4 rounded-xl border border-gray-100 dark:border-gray-800 hover:border-gray-200 dark:hover:border-gray-700 transition bg-white dark:bg-gray-850"
>
	<!-- Header -->
	<div class="flex items-start justify-between gap-2">
		<div class="flex items-start gap-3 flex-1 min-w-0">
			<!-- Type Icon -->
			<div class="text-2xl flex-shrink-0 mt-0.5">
				{getTypeIcon(server.type)}
			</div>

			<!-- Server Info -->
			<div class="flex-1 min-w-0">
				<div class="flex items-center gap-2 mb-1">
					<h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
						{server.name}
					</h3>

					<!-- Health Status Indicator -->
					<Tooltip content={server.health_status || 'unknown'}>
						<div class="flex items-center gap-1.5">
							<div class={`w-2 h-2 rounded-full ${getHealthStatusColor(server.health_status)}`} />
						</div>
					</Tooltip>

					<!-- Enabled Badge -->
					{#if !server.enabled}
						<span
							class="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
						>
							{$i18n.t('Disabled')}
						</span>
					{/if}

					<!-- Global Badge -->
					{#if server.is_global}
						<span
							class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
						>
							{$i18n.t('Global')}
						</span>
					{/if}
				</div>

				<!-- Description -->
				{#if server.description}
					<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
						{server.description}
					</p>
				{/if}

				<!-- Server Details -->
				<div class="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-500">
					<span class="flex items-center gap-1">
						<span class="font-medium">{$i18n.t('Type')}:</span>
						<span>{server.type}</span>
					</span>

					{#if server.command}
						<span class="flex items-center gap-1">
							<span class="font-medium">{$i18n.t('Command')}:</span>
							<code class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">
								{server.command}
							</code>
						</span>
					{/if}

					{#if server.url}
						<span class="flex items-center gap-1">
							<span class="font-medium">{$i18n.t('URL')}:</span>
							<code class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 truncate max-w-xs">
								{server.url}
							</code>
						</span>
					{/if}

					{#if server.last_health_check}
						<span class="flex items-center gap-1">
							<span class="font-medium">{$i18n.t('Last Check')}:</span>
							<span>{formatTimestamp(server.last_health_check)}</span>
						</span>
					{/if}
				</div>
			</div>
		</div>

		<!-- Menu Button -->
		{#if canEdit}
			<div class="relative flex-shrink-0">
				<button
					class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition opacity-0 group-hover:opacity-100"
					on:click={() => (showMenu = !showMenu)}
				>
					<EllipsisHorizontal className="size-4" />
				</button>

				{#if showMenu}
					<div
						class="absolute right-0 mt-1 w-48 rounded-lg shadow-lg bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-700 z-10"
						on:mouseleave={() => (showMenu = false)}
					>
						<div class="py-1">
							<button
								class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition"
								on:click={() => {
									dispatch('edit');
									showMenu = false;
								}}
							>
								{$i18n.t('Edit')}
							</button>

							<button
								class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition"
								on:click={() => {
									dispatch('toggleEnabled');
									showMenu = false;
								}}
							>
								{server.enabled ? $i18n.t('Disable') : $i18n.t('Enable')}
							</button>

							{#if $user?.role === 'admin'}
								<button
									class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition"
									on:click={() => {
										dispatch('toggleGlobal');
										showMenu = false;
									}}
								>
									{server.is_global ? $i18n.t('Make Private') : $i18n.t('Make Global')}
								</button>
							{/if}

							<hr class="my-1 border-gray-200 dark:border-gray-700" />

							<button
								class="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
								on:click={() => {
									dispatch('delete');
									showMenu = false;
								}}
							>
								{$i18n.t('Delete')}
							</button>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Server Info (if available) -->
	{#if server.server_info}
		<div
			class="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-500 pl-11 pt-1 border-t border-gray-100 dark:border-gray-800"
		>
			{#if server.server_info.server_name}
				<span class="flex items-center gap-1">
					<span class="font-medium">{$i18n.t('Server Name')}:</span>
					<span>{server.server_info.server_name}</span>
				</span>
			{/if}

			{#if server.server_info.server_version}
				<span class="flex items-center gap-1">
					<span class="font-medium">{$i18n.t('Version')}:</span>
					<span>{server.server_info.server_version}</span>
				</span>
			{/if}

			{#if server.server_info.protocol_version}
				<span class="flex items-center gap-1">
					<span class="font-medium">{$i18n.t('Protocol')}:</span>
					<span>{server.server_info.protocol_version}</span>
				</span>
			{/if}
		</div>
	{/if}

	<!-- Action Buttons -->
	<div class="flex items-center gap-2 pl-11">
		<button
			class="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium flex items-center gap-1.5"
			on:click={() => dispatch('healthCheck')}
			disabled={healthChecking}
		>
			{#if healthChecking}
				<Spinner className="size-3" />
			{:else}
				<span>🩺</span>
			{/if}
			<span>{$i18n.t('Health Check')}</span>
		</button>

		<button
			class="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium flex items-center gap-1.5"
			on:click={() => dispatch('viewResources')}
		>
			<span>📚</span>
			<span>{$i18n.t('Resources')}</span>
		</button>

		<button
			class="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium flex items-center gap-1.5"
			on:click={() => dispatch('viewTools')}
		>
			<span>🔧</span>
			<span>{$i18n.t('Tools')}</span>
		</button>
	</div>
</div>
