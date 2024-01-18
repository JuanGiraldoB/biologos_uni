new Vue({
  el: '#app',
  components: {
  	'time-slider':TimeSlider,
  },
	data: () => ({
		curTime: new Date(Date.now()).toTimeString().slice(0,5)
	}),
		mounted: function () {
	},
	methods:{
  	shiftTime(a) {
      this.curTime = a;
    }
	}	
});