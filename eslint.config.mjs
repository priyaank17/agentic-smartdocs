import eslintPluginJsonc from 'eslint-plugin-jsonc';
import eslintPluginJsonSchemaValidator from "eslint-plugin-json-schema-validator";


export default [

  ...eslintPluginJsonc.configs['flat/recommended-with-jsonc'],
  ...eslintPluginJsonSchemaValidator.configs["flat/recommended"],
  {
    ignores: ["node_modules/**", ".env/**", ".venv/**", ".venv"],
    rules: {
      // override/add rules settings here, such as:
      // 'jsonc/rule-name': 'error'
    }
  }
];
