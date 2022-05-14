const axios = require('axios');
const querystring = require('querystring');

class Postman {
  config = {
    apiKey: null,
    workspaceId: null,
    apiBaseUrl: 'https://api.getpostman.com'
  };

  constructor(apiKey, workspaceId = null) {
    this.config.apiKey = apiKey;
    this.config.workspaceId = workspaceId;
  }

  async request(method = 'get', path, params = null, data = null) {
    try {
      const options = {
        method,
        url: `${this.config.apiBaseUrl}/${path}?${querystring.stringify(params)}`,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.config.apiKey
        },
        data: data ? JSON.stringify(data) : null
      };

      const result = await axios(options);
      return result.data;
    } catch (err) {
      console.error(err.response.data)
      throw new Error(`${err.response.status} (${err.response.statusText}) while performing a ${method} on ${path}`);
    }
  }

  async get(path, params) {
    return await this.request('get', path, params);
  }

  async post(path, params, data) {
    return await this.request('post', path, params, data);
  }

  async put(path, params, data) {
    return await this.request('put', path, params, data);
  }

  async delete(path, params) {
    return await this.request('delete', path, params);
  }

  async apis(filter = null) {
    let {
      apis
    } = await this.get('apis', {
      workspace: this.config.workspaceId
    });
    if (filter) {
      apis = apis.filter(filter);
    }
    return apis;
  }

  async createAPI(data = {}) {
    const {
      api
    } = await this.post('apis', {
      workspace: this.config.workspaceId
    }, {
      api: data
    });
  }

  async updateAPI(apiId, data = {}) {
    const {
      api
    } = await this.put(`apis/${apiId}`, null, {
      api: data
    })
    return api;
  }

  async apiVersion(apiId, apiVersionId) {
    let {
      version
    } = await this.get(`apis/${apiId}/versions/${apiVersionId}`);
    return version;
  }

  async apiVersions(apiId, filter = null) {
    let {
      versions
    } = await this.get(`apis/${apiId}/versions`);
    if (filter) {
      versions = versions.filter(filter);
    }
    return versions;
  }

  async createAPIVersion(apiId, versionName = null) {
    const {
      version
    } = await this.post(`apis/${apiId}/versions`, null, {
      version: {
        name: versionName
      }
    });
    return version;
  }

  async createAPISchema(apiId, apiVersionId, schema = null) {
    const data = await this.post(`apis/${apiId}/versions/${apiVersionId}/schemas`, null, {
      schema: {
        type: 'openapi3',
        language: 'json',
        schema: JSON.stringify(schema)
      }
    });
    return data;
  }

  async updateAPISchema(apiId, apiVersionId, schemaId, schema = null) {
    const data = await this.put(`apis/${apiId}/versions/${apiVersionId}/schemas/${schemaId}`, null, {
      schema: {
        type: 'openapi3',
        language: 'json',
        schema: JSON.stringify(schema)
      }
    });
    return data;
  }

  async getDocumentationRelations(apiId, apiVersionId) {
    const data = await this.get(`apis/${apiId}/versions/${apiVersionId}/documentation`, null);
    return data;
  }

  async generateCollections(apiId, apiVersionId, schemaId, apiVersion) {
    const data = await this.post(`apis/${apiId}/versions/${apiVersionId}/schemas/${schemaId}/collections`, {
      workspace: this.config.workspaceId
    }, {
      name: `EmoDiary - ${apiVersion}`,
      relations: [{
        "type": "documentation"
      }]
    });
    return data;
  }

  async syncCollection(apiId, apiVersionId, entityId) {
    const data = await this.put(`apis/${apiId}/versions/${apiVersionId}/documentation/${entityId}/syncWithSchema`, null, null);
    return data;
  }

  async deleteCollection(collection_uid) {
    const data = await this.delete(`collections/${collection_uid}`, null);
    return data;
  }
}

module.exports = Postman;