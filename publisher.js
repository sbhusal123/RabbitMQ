const amqp = require("amqplib");

const msg = {number: process.argv[2]}

connect();

// Create a connection to the server
async function connect(){
    try{
        // Establish a connection to the Queuing Server
        const connection = await amqp.connect("amqp://localhost:5672");

        // Create a channel to pass a message
        const channel = await connection.createChannel();

        // Create a queue named jobs in a channel if doesn't exists
        const result = await channel.assertQueue("jobs");

        let stringified_msg = JSON.stringify(msg);

        // Send message to a queue named jobs
        channel.sendToQueue("jobs", Buffer.from(stringified_msg));

        console.log(`Job Send Succesfully ${msg.number}`);

    }

    catch(ex){
        console.error(ex)
    }
}