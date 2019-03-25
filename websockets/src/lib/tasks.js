Task.prototype.__proto__ = events.EventEmitter.prototype;
function BzcomplianceTask() {
   var self = this;

   self.run = function() {
      console.log("Running reporting task");
   }
}

function Task(data) {
   var self = this;
   self.data = data;
   events.EventEmitter.call(this);

   self.init = function() {
      if (self.data.task.type == 'task1') {
         self.task = new tasks.bzcompliance()
      } else {
         console.log("Task isn't defined");
      }
   }

   self.start = function() {
      console.log("Task called " + self.data.task.type);
      process.nextTick(function() {
         self.emit('start', self.data);
         self.run();
      });
   }

   self.run = function() {
         process.nextTick(function() {
            console.log("Task is running " + self.data.task.type);
            self.task.run();
            self.emit('done', self.data);
         });

   }

   self.init();
   //this.start();
}
   //socket.on('task', function(data) {
      //data.toastr = {
            //"closeButton": true,
            //"debug": false,
            //"progressBar": false,
            //"positionClass": "toast-top-right",
            //"showDuration": "1000",
            //"hideDuration": "1000",
            //"timeOut": "7000",
            //"extendedTimeOut": "1000",
            //"showEasing": "swing",
            //"hideEasing": "linear",
            //"showMethod": "fadeIn",
            //"hideMethod": "fadeOut"
      //};
      //var allTask = [
         //{
            //task: {
               //type: 'task1',
            //},
         //},
         //{
            //task: {
               //type: 'task2',
            //},
         //},
      //];

      //var definedTasks = []
      //for(var i = 0; i < allTask.length; i++) {
         //var task = new Task(allTask[i]);

         //task.on('call', function(data) {
            //console.log('Done Calling ' + data.task.type);
         //});
         
         //task.on('run', function(data) {
            //console.log('Done Running ' + data.task.type);
         //});

         //definedTasks.push(task);
      //}

      //for(var i = 0; i < definedTasks.length; i++) {
         //definedTasks[i].start();
      //}
      //console.log("Done calling tasks");
   //});

         // logic for running tasks
       // 	//data.time = time;
       // 	data.type = 'success';   	

       // 	//setTimeout(callTask, 1000);
       // } else if (data.task.type == 'task2') {
            
       // 	data.type = 'info';

       // 	//setTimeout(callback, 1000, checkTime);
       // } else if (data.task.type == 'task3') {
       
       // 	data.type = 'warning';

       // 	//setTimeout(callback, 1000, checkTime);
       // } else if (data.task.type == 'task4') {
          
       // 	data.type = 'warning';

       // 	//setTimeout(callback, 1000, checkTime);
       // } else {

       // 	io.emit('error', data);

       // }
