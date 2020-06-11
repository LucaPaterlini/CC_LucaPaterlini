# Order book implementation python3 version1
Note all the cost are on time in its worst case scenario.

In the simple version in python 3 the assumption is no action will be taken
in case the max of the bid is greater than the min of the ask.

The second assumption is the cancel operation is that cancel of an order have a lower priority
than getting the latest get_best_bid_and_ask.


The aim of this solution its the simplicity and readability.

The solution have O(1) cost in time for adding or updating an order and getting the latest best bid and ask.
While it have O(n) in the cancel operation.

# Future development golang version 2

## Requirements

1. Adding the execution of compatible orders on the crests of both sides of the book
1.1 Keeping a journal of the executed orders
2. Correct execution assuming orders unordered by time
3. Reduce the cancel cost to O(log(n)) paying the price of it by increasing the add cost to O(log(n)) 
4. making the class accessible concurrently 



### Proposed Structure 

```
type AllOrderBook = struct{
     orders = struct {
        data sync.Map
        locker sync.RWmutex
     }
     listBooks = []OrderBook
}

type OrderBook = struct {
    buy LinkedListOrders
    buyLocker sync.RWmutex
    sell LinkedListOrders
    sellLocker sync.RWmutex
}

```
    
## Idea of implementation

1.To satisfy the first and the 1.1 requirement a solution its to have a dictionary of objects for each ticker 
that contains 2 skip lists (ordered list data structure) on the bid and ask sides in order to be able to parse 
from the crest the bottom both sides and reducing the orders size until the matching order is satisfied.

Specifically for the second requirement a linked list can be added to the main orderbook class and update it with
the executed orders, at the same time to keep the data structure consistent a new field executed (int) should be added
to each order that indicate how many unit of the order has been executed(Shares,barrels,etc).

2. using the skip list having as key of sorting price and second key time allow keep the execution consistent even if few 
orders has been delivered in delay compared to their execution, it can be useful in case a verify its
need at the end of the trading session to certify the right execution.

3. Changing the time execution cost:
  - automatic execution on add or update on a fully executed order O(N): worst case scenario an order matching the entire book.
  - add O(log(n)): dependent from insertion of the order in the skip list.
  - update O(1): keeping a dictionary of pointer to each order its possible to have this cost.
  - cancel O(log(n)): due to the find of the item in the skip list.
  - get_best_bid_and_ask O(1): both elements are at the ends of their skip list.  



4. To make the Class usable in a concurrency program I have added the mutex to use while doing update on a specific order
 in AllOrderBook and a locker for each side of the book to use to create a cs around their structure every time its accessed.
 I could have done it more gradually creating a cs around each order but my assumption its that having so would not give any greater
 improvement if the tickers are ominously distributed on bid and ask side assuming a number of cores inferior of the number
 of (ticker,side) tuple  getting accessed concurrently.
 
 ## Doing better 
 
 Both solutions mentioned earlier have as cost in memory O(n) where n is the number of the active orders.
 
 What we can do if we can relax the 5 decimal requirement or reduce the distance in price an order can be placed from the current 
 or increase the available ram on our server in order to be able to use a big array without incurring in memory swap 
 or pagination(eg. for [NYSE:BRK.A](https://g.co/kgs/NUD3oc)  the span could be 1million$ to 0.00001 meaning 100 billion 
 long array of pointer of 64 bit, meaning around 2x800 gb ram for both sides if the 5 decimal requirement its untouched).
 
 If this is the case an array of pointer to linked list of orders could be a viable solution, considering
 that have as cost in memory O(m+n)where n is the number of orders and where m is the fixed max price can be offered or requested for
 a specific share multiplied by 10 at its decimal as per the previous example.
 If freeing memory on cancel its required instead, a substitution of the single linked list structure with the double linked list
 will consent having a pointer to the item to cancel to access its previous element and make it point to the item following
 the on to cancel.
 
 
 Execution cost:
  - automatic execution on add or update on a fully executed order O(N): worst case scenario an order matching the entire book.
  - add O(1): adding one item to the linked list tail of its specific price point
  - update O(1): keeping a dictionary of pointer to each order its possible to have this cost. (unchanged version 2)
  - cancel O(1): use the same mechanism of update and set the size of the order to 0.
  - get_best_bid_and_ask O(1): two pointers to the tail and the head of bid and ask are kept, updated every add or update or cancel
  if required. 
 
 There was a contest on this specific problem  [Quant Cup 1](https://web.archive.org/web/20140529180725/http://www.quantcup.org/)
 and this was the  [winning implementation](https://web.archive.org/web/20141222151051/https://dl.dropboxusercontent.com/u/3001534/engine.c) (2011)
 
 
 P.s. when I started this readme I thought that was not available and off the shelf solution on aws
 [x1e.32xlarge](https://aws.amazon.com/ec2/pricing/on-demand/) that fit the previously mentioned example of order book.
 
 ### Architectural notes
 
This exercise require to store all the ticker data structure in a bigger data structure,
a good idea could be creating a set of docker container one for each supported ticker and stream to each
of them only relevant order for itself.
As well this would improve the scalability having as hw limit the max ram required from a single order book
instead of the sum of all of them and having the possibility to locate the containers on different hw machines
in the most convenient way.
