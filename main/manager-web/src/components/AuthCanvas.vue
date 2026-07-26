<template>
  <div class="auth-canvas" aria-hidden="true">
    <!-- 极光渐变色域 -->
    <div class="aurora aurora-a" :style="layerStyle(26)"></div>
    <div class="aurora aurora-b" :style="layerStyle(-18)"></div>
    <div class="aurora aurora-c" :style="layerStyle(12)"></div>

    <!-- 透视网格地平面 -->
    <div class="grid-floor"></div>

    <!-- 心电图生命线 -->
    <svg class="ecg" viewBox="0 0 1440 160" preserveAspectRatio="none">
      <path class="ecg-ghost" :d="ecgPath" />
      <path class="ecg-line" :d="ecgPath" />
    </svg>

    <!-- 慢速漂浮的十字符号阵 -->
    <div
      v-for="(c, i) in crosses"
      :key="'cross-' + i"
      class="drift-cross"
      :style="crossStyle(c)"
    >
      <lucide-icon name="cross" :size="c.size" :stroke-width="1.4" />
    </div>

    <!-- 颗粒噪点 -->
    <svg class="noise" width="100%" height="100%">
      <filter id="authNoise">
        <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#authNoise)" />
    </svg>

    <!-- 暗角 -->
    <div class="vignette"></div>
  </div>
</template>

<script>
import LucideIcon from './LucideIcon.vue';

const ECG_PATH =
  'M0,90 L160,90 L200,90 L214,64 L228,110 L240,90 L340,90 L368,90 L380,74 L392,90 ' +
  'L520,90 L560,90 L574,30 L590,140 L604,90 L724,90 L820,90 L834,72 L848,102 L860,90 ' +
  'L980,90 L1020,90 L1034,52 L1050,126 L1064,90 L1200,90 L1290,90 L1304,70 L1318,104 L1330,90 L1440,90';

export default {
  name: 'AuthCanvas',
  components: { LucideIcon },
  data() {
    return {
      ecgPath: ECG_PATH,
      // 鼠标视差（经 rAF 平滑插值）
      mx: 0,
      my: 0,
      tx: 0,
      ty: 0,
      rafId: null,
      reduceMotion: false,
      crosses: [
        { x: 8, y: 18, size: 14, dur: 26, delay: 0, opacity: 0.16 },
        { x: 22, y: 72, size: 10, dur: 32, delay: -8, opacity: 0.1 },
        { x: 46, y: 12, size: 12, dur: 28, delay: -14, opacity: 0.12 },
        { x: 68, y: 64, size: 16, dur: 36, delay: -4, opacity: 0.1 },
        { x: 86, y: 26, size: 10, dur: 30, delay: -20, opacity: 0.14 },
        { x: 94, y: 78, size: 12, dur: 24, delay: -10, opacity: 0.1 },
      ],
    };
  },
  mounted() {
    this.reduceMotion =
      window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!this.reduceMotion) {
      window.addEventListener('mousemove', this.onMove, { passive: true });
      this.tick();
    }
  },
  beforeDestroy() {
    window.removeEventListener('mousemove', this.onMove);
    if (this.rafId) cancelAnimationFrame(this.rafId);
  },
  methods: {
    onMove(e) {
      this.tx = e.clientX / window.innerWidth - 0.5;
      this.ty = e.clientY / window.innerHeight - 0.5;
    },
    tick() {
      // 线性插值实现物理惯性感
      this.mx += (this.tx - this.mx) * 0.06;
      this.my += (this.ty - this.my) * 0.06;
      this.rafId = requestAnimationFrame(this.tick);
    },
    layerStyle(depth) {
      if (this.reduceMotion) return {};
      return {
        transform: `translate3d(${this.mx * depth}px, ${this.my * depth}px, 0)`,
      };
    },
    crossStyle(c) {
      return {
        left: c.x + '%',
        top: c.y + '%',
        opacity: c.opacity,
        animationDuration: c.dur + 's',
        animationDelay: c.delay + 's',
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.auth-canvas {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background:
    radial-gradient(120% 90% at 78% -10%, #0c2740 0%, transparent 55%),
    radial-gradient(90% 70% at 8% 110%, #071e2e 0%, transparent 55%),
    #04070f;
  pointer-events: none;
}

.aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  will-change: transform;
}

.aurora-a {
  width: 56vw;
  height: 56vw;
  left: -14vw;
  top: -22vw;
  background: radial-gradient(circle at 40% 40%, rgba(45, 212, 191, 0.34), transparent 62%);
  animation: aurora-drift 22s ease-in-out infinite alternate;
}

.aurora-b {
  width: 48vw;
  height: 48vw;
  right: -16vw;
  top: 4vh;
  background: radial-gradient(circle at 55% 45%, rgba(79, 124, 255, 0.3), transparent 60%);
  animation: aurora-drift 28s ease-in-out -6s infinite alternate-reverse;
}

.aurora-c {
  width: 42vw;
  height: 42vw;
  left: 28vw;
  bottom: -24vw;
  background: radial-gradient(circle at 50% 50%, rgba(34, 211, 238, 0.2), transparent 60%);
  animation: aurora-drift 26s ease-in-out -12s infinite alternate;
}

@keyframes aurora-drift {
  from {
    margin-left: 0;
    margin-top: 0;
  }
  to {
    margin-left: 6vw;
    margin-top: 4vh;
  }
}

.grid-floor {
  position: absolute;
  left: -20%;
  right: -20%;
  bottom: -32%;
  height: 70%;
  background-image:
    linear-gradient(rgba(94, 234, 212, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(94, 234, 212, 0.07) 1px, transparent 1px);
  background-size: 56px 56px;
  transform: perspective(620px) rotateX(64deg);
  transform-origin: center top;
  mask-image: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent 85%);
  -webkit-mask-image: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent 85%);
}

.ecg {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 12vh;
  width: 100%;
  height: 160px;
  opacity: 0.85;

  path {
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .ecg-ghost {
    stroke: rgba(45, 212, 191, 0.12);
    stroke-width: 1.5;
  }

  .ecg-line {
    stroke: #2dd4bf;
    stroke-width: 2;
    stroke-dasharray: 260 3400;
    stroke-dashoffset: 3660;
    filter: drop-shadow(0 0 6px rgba(45, 212, 191, 0.9));
    animation: ecg-run 7s linear infinite;
  }
}

@keyframes ecg-run {
  to {
    stroke-dashoffset: 0;
  }
}

.drift-cross {
  position: absolute;
  color: #5eead4;
  animation-name: cross-float;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}

@keyframes cross-float {
  0%,
  100% {
    transform: translate3d(0, 0, 0) rotate(0deg);
  }
  50% {
    transform: translate3d(14px, -22px, 0) rotate(10deg);
  }
}

.noise {
  position: absolute;
  inset: 0;
  opacity: 0.05;
  mix-blend-mode: overlay;
}

.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(120% 100% at 50% 40%, transparent 55%, rgba(2, 4, 10, 0.75) 100%);
}

@media (prefers-reduced-motion: reduce) {
  .aurora,
  .ecg-line,
  .drift-cross {
    animation: none;
  }
}
</style>
