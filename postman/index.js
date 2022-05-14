#!/usr/bin/env node

const SwaggerParser = require('@apidevtools/swagger-parser');
const Postman = require('./helper/postman-sdk');
const path = require('node:path');

const envFilePath = path.join(__dirname, '..', '.env')
require('dotenv').config({
  path: envFilePath
})

const postman = new Postman(
  process.env.POSTMAN_API_KEY,
  process.env.POSTMAN_WORKSPACE_ID
);

const openApiPath = path.join(__dirname, '..', 'openapi.json');

(async () => {
  try {
    console.info("Generating postman api and collection from " + openApiPath)
    const localAPI = await SwaggerParser.parse(openApiPath);

    // Obtain a remote representation of the API
    // defined by the local OpenAPI specification.
    console.info("Obtaining a remote representation of the api defined by the local OpenAPI specification.")
    let remoteAPI = await postman.apis(api => api.name == localAPI.info.title);
    if (!remoteAPI.length) {
      remoteAPI = await postman.createAPI({
        name: localAPI.info.title,
        description: localAPI.info.description
      });
    } else {
      remoteAPI = remoteAPI[0];
      if (remoteAPI.name != localAPI.info.title ||
        remoteAPI.description != localAPI.info.description) {
        remoteAPI = await postman.updateAPI(remoteAPI.id, {
          name: localAPI.info.title,
          description: localAPI.info.description
        });
      }
    }

    // Obtain a remote representation of the API version
    // defined by the local OpenAPI specification.
    console.info("Obtaining a remote representation of the api version defined by the local OpenAPI specification.")
    let remoteAPIVersion = await postman.apiVersions(remoteAPI.id, version => version.name == localAPI.info.version);
    if (!remoteAPIVersion.length) {
      remoteAPIVersion = await postman.createAPIVersion(remoteAPI.id, localAPI.info.version);
      remoteAPIVersion.schema = [];
    } else {
      remoteAPIVersion = await postman.apiVersion(remoteAPI.id, remoteAPIVersion[0].id);
    }

    // Synchronize the remote API schema with the one
    // defined by the local OpenAPI specification.
    console.info("Synchronize the remote API schema with the one defined by the local OpenAPI specification.")
    let schemaUpdate
    if (!remoteAPIVersion.schema.length) {
      schemaUpdate = await postman.createAPISchema(remoteAPI.id, remoteAPIVersion.id, localAPI);
    } else {
      schemaUpdate = await postman.updateAPISchema(remoteAPI.id, remoteAPIVersion.id, remoteAPIVersion.schema[0], localAPI);
    }

    // Syncing collection to api schema
    console.info("Syncing collection to api schema")
    let getDocumentationCollections = await postman.getDocumentationRelations(remoteAPI.id, remoteAPIVersion.id)
    if (!getDocumentationCollections.documentation.length) {
      let response = await postman.generateCollections(remoteAPI.id, remoteAPIVersion.id, schemaUpdate.schema.id, remoteAPIVersion.name)
    } else {
      let response = await postman.syncCollection(remoteAPI.id, remoteAPIVersion.id, getDocumentationCollections.documentation[0].id)
    }
    console.info("Finishing generating api and collection")
  } catch (err) {
    console.error(err);
  }
})();