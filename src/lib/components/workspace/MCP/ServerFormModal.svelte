<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import type { MCPServer, MCPServerForm } from '$lib/apis/mcp';
	import Modal from '../../common/Modal.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let server: MCPServer | null = null;
	export let mode: 'create' | 'edit' = 'create';

	let formData: MCPServerForm = {
		name: '',
		description: '',
		type: 'stdio',
		command: '',
		args: [],
		url: '',
		env: {},
		auth_type: '',
		auth_config: {},
		is_global: false,
		meta: {}
	};

	let argsText = '';
	let envText = '';

	$: if (show && server && mode === 'edit') {
		formData = {
			name: server.name,
			description: server.description || '',
			type: server.type,
			command: server.command || '',
			args: server.args || [],
			url: server.url || '',
			env: server.env || {},
			auth_type: server.auth_type || '',
			auth_config: server.auth_config || {},
			is_global: server.is_global,
			meta: server.meta || {}
		};
		argsText = (server.args || []).join('\n');
		envText = server.env ? Object.entries(server.env).map(([k, v]) => `${k}=${v}`).join('\n') : '';
	} else if (show && mode === 'create') {
		formData = {
			name: '',
			description: '',
			type: 'stdio',
			command: '',
			args: [],
			url: '',
			env: {},
			auth_type: '',
			auth_config: {},
			is_global: false,
			meta: {}
		};
		argsText = '';
		envText = '';
	}

	const handleSubmit = () => {
		// Parse args from text
		formData.args = argsText
			.split('\n')
			.map(line => line.trim())
			.filter(line => line.length > 0);

		// Parse env from text
		const envPairs = envText
			.split('\n')
			.map(line => line.trim())
			.filter(line => line.length > 0 && line.includes('='));

		formData.env = {};
		for (const pair of envPairs) {
			const [key, ...valueParts] = pair.split('=');
			if (key) {
				formData.env[key.trim()] = valueParts.join('=').trim();
			}
		}

		dispatch('submit', formData);
	};

	const handleCancel = () => {
		show = false;
	};
</script>

{#if show}
	<Modal
		size="lg"
		on:close={() => {
			show = false;
		}}
	>
		<div class="p-6">
			<div class="mb-4">
				<h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
					{mode === 'create' ? $i18n.t('Create MCP Server') : $i18n.t('Edit MCP Server')}
				</h2>
			</div>

			<form on:submit|preventDefault={handleSubmit} class="space-y-4">
				<!-- Name -->
				<div>
					<label
						for="name"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
					>
						{$i18n.t('Name')} <span class="text-red-500">*</span>
					</label>
					<input
						id="name"
						type="text"
						bind:value={formData.name}
						required
						class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
						placeholder={$i18n.t('My MCP Server')}
					/>
				</div>

				<!-- Description -->
				<div>
					<label
						for="description"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
					>
						{$i18n.t('Description')}
					</label>
					<textarea
						id="description"
						bind:value={formData.description}
						rows="2"
						class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
						placeholder={$i18n.t('Brief description of this MCP server')}
					/>
				</div>

				<!-- Type -->
				<div>
					<label
						for="type"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
					>
						{$i18n.t('Transport Type')} <span class="text-red-500">*</span>
					</label>
					<select
						id="type"
						bind:value={formData.type}
						required
						class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
					>
						<option value="stdio">{$i18n.t('Stdio (Local Process)')}</option>
						<option value="sse">{$i18n.t('SSE (Server-Sent Events)')}</option>
						<option value="streamable_http">{$i18n.t('HTTP (Streamable HTTP)')}</option>
					</select>
				</div>

				<!-- Stdio Configuration -->
				{#if formData.type === 'stdio'}
					<div class="space-y-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-850">
						<div>
							<label
								for="command"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								{$i18n.t('Command')} <span class="text-red-500">*</span>
							</label>
							<input
								id="command"
								type="text"
								bind:value={formData.command}
								required
								class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
								placeholder={$i18n.t('python')}
							/>
						</div>

						<div>
							<label
								for="args"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								{$i18n.t('Arguments (one per line)')}
							</label>
							<textarea
								id="args"
								bind:value={argsText}
								rows="4"
								class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 font-mono text-sm"
								placeholder="-m&#10;mcp_server&#10;--config&#10;config.json"
							/>
						</div>

						<div>
							<label
								for="env"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								{$i18n.t('Environment Variables (KEY=VALUE, one per line)')}
							</label>
							<textarea
								id="env"
								bind:value={envText}
								rows="4"
								class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 font-mono text-sm"
								placeholder="API_KEY=your_key_here&#10;DEBUG=true"
							/>
						</div>
					</div>
				{/if}

				<!-- SSE/HTTP Configuration -->
				{#if formData.type === 'sse' || formData.type === 'streamable_http'}
					<div class="space-y-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-850">
						<div>
							<label
								for="url"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								{$i18n.t('URL')} <span class="text-red-500">*</span>
							</label>
							<input
								id="url"
								type="url"
								bind:value={formData.url}
								required
								class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
								placeholder={formData.type === 'sse'
									? 'http://localhost:3001/sse'
									: 'http://localhost:3001/mcp'}
							/>
						</div>

						<div>
							<label
								for="auth_type"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								{$i18n.t('Authentication Type')}
							</label>
							<select
								id="auth_type"
								bind:value={formData.auth_type}
								class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
							>
								<option value="">{$i18n.t('None')}</option>
								<option value="bearer">{$i18n.t('Bearer Token')}</option>
								<option value="basic">{$i18n.t('Basic Auth')}</option>
								<option value="api_key">{$i18n.t('API Key')}</option>
							</select>
						</div>
					</div>
				{/if}

				<!-- Global Access (Admin Only) -->
				<div class="flex items-center gap-2">
					<input
						id="is_global"
						type="checkbox"
						bind:checked={formData.is_global}
						class="w-4 h-4 rounded border-gray-300 dark:border-gray-700 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-600"
					/>
					<label
						for="is_global"
						class="text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$i18n.t('Make this server available to all users (global)')}
					</label>
				</div>

				<!-- Form Actions -->
				<div class="flex justify-end gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
					<button
						type="button"
						on:click={handleCancel}
						class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition font-medium"
					>
						{$i18n.t('Cancel')}
					</button>
					<button
						type="submit"
						class="px-4 py-2 rounded-lg bg-black text-white dark:bg-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200 transition font-medium"
					>
						{mode === 'create' ? $i18n.t('Create') : $i18n.t('Save')}
					</button>
				</div>
			</form>
		</div>
	</Modal>
{/if}
