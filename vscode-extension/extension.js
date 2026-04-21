const path = require('path');
const vscode = require('vscode');

let client;

function activate(context) {
  let LanguageClient;
  let TransportKind;

  try {
    const lcNode = require('vscode-languageclient/node');
    LanguageClient = lcNode.LanguageClient;
    TransportKind = lcNode.TransportKind;
  } catch (err) {
    vscode.window.showInformationMessage(
      'ypool: vscode-languageclient is not installed. ' +
      'Run "npm install" in the extension folder to enable live error checking. ' +
      'Syntax highlighting is still active.'
    );
    return;
  }

  const config = vscode.workspace.getConfiguration('ypool');
  const pythonPath = config.get('pythonPath') || 'python';
  const serverScript = context.asAbsolutePath(path.join('server', 'server.py'));

  const serverOptions = {
    command: pythonPath,
    args: [serverScript],
    transport: TransportKind.stdio
  };

  const clientOptions = {
    documentSelector: [{ scheme: 'file', language: 'ypool' }],
    synchronize: {
      configurationSection: 'ypool'
    }
  };

  client = new LanguageClient(
    'ypool',
    'ypool Language Server',
    serverOptions,
    clientOptions
  );

  client.start();
  context.subscriptions.push(client);
}

function deactivate() {
  return client?.stop();
}

module.exports = { activate, deactivate };
