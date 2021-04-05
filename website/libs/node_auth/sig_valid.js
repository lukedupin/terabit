const ethUtil = require('ethereumjs-util');
const sigUtil = require('eth-sig-util');

if ( process.argv.length != 5 ) {
    console.log(`node ${process.argv[1]} public nonce`);
    process.exit(-1);
    return;
}

const publicAddress = process.argv[2];
const nonce = process.argv[3];
const sig = process.argv[4];

const data = [{
    type: 'string',
    name: 'Reason',
    value: 'Please confirm you own this account by signing the nonce. For more information: https://en.wikipedia.org/wiki/Cryptographic_nonce'
},
{
    type: 'string',
    name: 'Nonce',
    value: nonce
}];

const recovered = sigUtil.recoverTypedSignature({ data, sig });
process.exit( (publicAddress.toLowerCase() === recovered.toLowerCase())? 0: 1 );
