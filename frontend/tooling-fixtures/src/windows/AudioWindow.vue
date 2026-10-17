<!-- Negative lint fixture: no <audio>, no <video> unless muted (Constitution §14.10). -->
<template>
  <audio src="beep.wav" />
  <video src="clip.mp4" />
  <video src="clip.mp4" :muted="false" />
</template>
