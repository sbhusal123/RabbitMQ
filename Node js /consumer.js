const amqp = require("amqplib");


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

        channel.consume("jobs", message=> {
            // Decode the message into string and Jsonify it
            const input = JSON.parse(message.content.toString());

            // If input number is 7 acknowledge(deque) from the Queue
            if(input.number == 7){
                channel.ack(message);
            }

            console.log(`Received job with  ${input.number}`);
        });



        console.log("Waiting For messages..");

    }

    catch(ex){
        console.error(ex)
    }
}