'use strict';
const shim = require('fabric-shim');
const util = require('util');

let Votechain = class {
    async Init(stub) {
        // use the instantiate input arguments to decide initial chaincode state values
        const args = stub.getFunctionAndParameters().params

        // save the initial states
        args.forEach(async arg => {
            await stub.putState(arg, Buffer.from("0"));
        })

        return shim.success(`Initialized Successfully with ${args.length} candidates`);
    }

    async Invoke(stub) {
        // use the invoke input arguments to decide intended changes
        console.info('Transaction ID: ' + stub.getTxID());
        console.info(util.format('Args: %j', stub.getArgs()));

        const args = stub.getFunctionAndParameters();

        const method = this[args.fcn];

        // Verifies if method exist
        if (!method) {
            return shim.error(`Method "${args.fcn}" doesn't exist`);
        }

        try {
            return await method(stub, args.params);
        } catch (err) {
            console.log(err.stack);
            return shim.error(err.message ? err.message : 'who knows the fuck has gone wrong');
        }
    }

    async GetResults(stub, args) {
        if (args.length != 0) {
            return shim.error("Incorrect number of arguments. Expected none");
        }
        try {
            var resultDict = {}
            var iterator = await stub.getStateByRange("", "");
            while (true) {
                const resource = await iterator.next();
                if (resource.value.getKey()) {
                    resultDict[resource.value.getKey()] = resource.value.getValue().toString("utf8");
                }
                if (resource.done) {   
                    await iterator.close();
                    break;
                }
            }
            var resultString = JSON.stringify(resultDict);
            return shim.success(Buffer.from(resultString));
        } catch (error) {
            console.log(error.stack);
            return shim.error(error.message);
        }
    }

    async GetResult(stub, args) {
        if (args.length != 1) {
            return shim.error("Incorrect number of arguments. Expected 1");
        }
        var candidate = args[0];
        try {
            var result = await stub.getState(candidate);
            return shim.success(Buffer.from(`{result: \"${Buffer.from(result).toString("utf8")}\"}`));
        } catch (error) {
            return shim.error(error.message);
        }
    }

    async SendVote(stub, args) {
        if (args.length != 1) {
            return shim.error("Incorrect number of arguments. Expecting 1");
        }
        var candidate = args[0]
        try {
            var state = Buffer.from(await stub.getState(candidate)).toString("utf8");
            var value = parseInt(state) + 1;
            await stub.putState(candidate, Buffer.from(value.toString()));
            var txId = stub.getTxID();
            var payload = Buffer.from(`{"txId": "${txId}"}`);
            return shim.success(payload);
        } catch (error) {
            return shim.error(error.message);
        }
    }

    async AddCandidates(stub, args) {
        if (args.length == 0) {
            return shim.error("Incorrect number of arguments. Expecting 1 or more");
        }
        try {
            args.forEach(async candidate => {
                await stub.putState(candidate, Buffer.from("0"));
            })
            var txId = stub.getTxID();
            var payload = Buffer.from(`{"txId": "${txId}"}`);
            return shim.success(payload);
        } catch (error) {
            return shim.error(error.message);
        }
    }

    async VerifyVote(stub, args) {
        if (args.length != 1) {
            return shim.error("Incorrect number of arguments. Expected 1 - transaction id");
        }
        var txId = args[0];
        try {
            var result = "";
            var keyIterator = await stub.getStateByRange("", "");
            while (true) {
                const resource = await keyIterator.next();
                try {
                    if (resource.value) {
                        var resourceKey = resource.value.getKey();
                        var historyIterator = await stub.getHistoryForKey(resourceKey);
                        while (true) {
                            const history = await historyIterator.next();
                            if (history.value && history.value.getTxId() === txId) {
                                result = resourceKey;
                            }
                            if (history.done) {   
                                await historyIterator.close();
                                break;
                            }
                        }
                    }
                } catch (error) {
                    console.log(error.message);
                }
                if (resource.done) {   
                    await keyIterator.close();
                    break;
                }
            }
            if (result == "") {
                return shim.error("{detail: \"Could not find the transaction in the ledger\"}");
            }
            return shim.success(Buffer.from(`{"candidate": "${result}"}`));
        } catch (error) {
            return shim.error(error.message);
        }
    }
};

shim.start(new Votechain());
