import { WEBUI_API_BASE_URL } from '$lib/constants';

// Types
export interface MCPServer {
	id: string;
	user_id: string;
	name: string;
	description?: string;
	type: 'stdio' | 'sse' | 'streamable_http';
	command?: string;
	args?: string[];
	url?: string;
	env?: Record<string, string>;
	auth_type?: string;
	auth_config?: Record<string, any>;
	enabled: boolean;
	is_global: boolean;
	health_status?: string;
	last_health_check?: number;
	server_info?: Record<string, any>;
	meta?: Record<string, any>;
	created_at: number;
	updated_at: number;
}

export interface MCPServerForm {
	name: string;
	description?: string;
	type: 'stdio' | 'sse' | 'streamable_http';
	command?: string;
	args?: string[];
	url?: string;
	env?: Record<string, string>;
	auth_type?: string;
	auth_config?: Record<string, any>;
	is_global?: boolean;
	meta?: Record<string, any>;
}

export interface MCPResource {
	uri: string;
	name?: string;
	description?: string;
	mimeType?: string;
}

export interface MCPTool {
	name: string;
	description?: string;
	inputSchema?: Record<string, any>;
}

export interface MCPPrompt {
	name: string;
	description?: string;
	arguments?: Array<{
		name: string;
		description?: string;
		required?: boolean;
	}>;
}

// Server Management APIs
export const getMCPServers = async (token: string = '') => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const createMCPServer = async (token: string, server: MCPServerForm) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getMCPServerById = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateMCPServerById = async (token: string, serverId: string, server: MCPServerForm) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'PUT',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteMCPServerById = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'DELETE',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const toggleMCPServerById = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/toggle`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const toggleMCPServerGlobalById = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/toggle/global`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Resource APIs
export const listMCPResources = async (token: string, serverId: string, refresh: boolean = false) => {
	let error = null;

	const res = await fetch(
		`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/resources${refresh ? '?refresh=true' : ''}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				authorization: `Bearer ${token}`
			}
		}
	)
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const readMCPResource = async (token: string, serverId: string, uri: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/resources/read`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ uri })
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const subscribeMCPResource = async (token: string, serverId: string, uri: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/resources/subscribe`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ uri })
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const unsubscribeMCPResource = async (token: string, serverId: string, uri: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/resources/unsubscribe`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ uri })
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Tool APIs
export const listMCPTools = async (token: string, serverId: string, refresh: boolean = false) => {
	let error = null;

	const res = await fetch(
		`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/tools${refresh ? '?refresh=true' : ''}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				authorization: `Bearer ${token}`
			}
		}
	)
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const callMCPTool = async (
	token: string,
	serverId: string,
	toolName: string,
	args: Record<string, any> = {}
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/tools/call`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			name: toolName,
			arguments: args
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Prompt APIs
export const listMCPPrompts = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/prompts`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getMCPPrompt = async (
	token: string,
	serverId: string,
	promptName: string,
	args: Record<string, any> = {}
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/prompts/get`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			name: promptName,
			arguments: args
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Health & Config APIs
export const checkMCPServerHealth = async (token: string, serverId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/health`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const generateMCPConfig = async (token: string, platform: string = 'standard') => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/config/generate?platform=${platform}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const downloadMCPConfig = async (token: string, platform: string = 'standard') => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/config/download?platform=${platform}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.blob();
		})
		.catch((err) => {
			error = err;
			console.error(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
