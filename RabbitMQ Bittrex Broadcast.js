// vim:sw=4:nu:expandtab:tabstop=4:ai

const spawn = require('threads').spawn;
var Threads = require('webworker-threads');
var t = Threads.create();

var args = process.argv.slice(2);
console.log(args)

var f = function(input, done) {
  var amqp = require('amqplib/callback_api')
  const MarketManager = require('bittrex-market')
  console.log('input: ', input)
  market = input['Market']
  console.log('Starting sender. Market:', market )
  amqp.connect('amqp://localhost', function(err, conn) {

    conn.createChannel(function(err, ch) {

      var ex = 'bittrex';
      var msg = '';

      ch.assertExchange(ex, 'fanout', {durable: false});
      const marketManager = new MarketManager(false)

      marketManager.market( market, (err, ethereum) => {
        ethereum.on('fills', console.log)

        ethereum.on('orderbookUpdated', () => {
          //console.log('Asks')
          //console.log(ethereum.asks.slice(1,5))
          var book = {}

          book['symbol'] = market
          book['timestamp'] = (new Date).getTime();
          book['askPx'] = ethereum.asks[0][0]
          book['askQty'] = ethereum.asks[0][1]

          book['bidPx'] = ethereum.bids[0][0]
          book['bidQty'] = ethereum.bids[0][1]

          var msg = new Buffer( JSON.stringify(book) );
          ch.publish( ex, '', msg )
          console.log( JSON.stringify(book) )
          //console.log('Bids')
          //console.log(ethereum.bids.slice(0,3))
        })

        //fires each time changes have been applied to the orderbook, and prints the changes only
        sides = ['asks', 'bids']
        eventTypes = ['removed', 'inserted', 'updated']
        sides.forEach((side) => {
          eventTypes.forEach((type) => {
            ethereum.on(`orderbook.diff.${side}.${type}`, (event) => {
              //console.log(side, type, event)
            })
          })        
        })
      })
    });
    //setTimeout(function() { conn.close();  }, 500);
  });
};

var thread1 = spawn(f)
var thread2 = spawn(f)

thread1.send({'Market':'BTC-ETH'})
thread2.send({'Market':'BTC-LTC'})

