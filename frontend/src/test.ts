// Test file for CI verification - has intentional lint errors

import { something } from './nonexistent';  // unused import

const unusedVariable = 'test';  // should trigger no-unused-vars

function testFunction(param: any) {  // should trigger no-explicit-any warning
  console.log('test');  // should trigger no-console warning
  return param;
}

export { testFunction };
