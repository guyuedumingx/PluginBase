我碰到了一个状态管理的大问题：

基于流的状态管理缺陷：在流的前后组件之间需要的依赖是不一样的，很难在流的头部将所需的所有状态都准备好，而在中间显示传递的状态只有一个`data`,这是远远不够的，比如流可能执行到中间的时候需要一个`item_onclick`函数，那么如果不在一开始就知道后面需要什么函数时，程序会有很多`bug`，如果想要一开始就准备好足够的依赖，一个困难是，有个依赖还没有生成，第二是传递的方式很丑陋，第三是依赖过多，严重冗余

解决方式：
尝试构建类似`redux`的触发是全局状态管理  
