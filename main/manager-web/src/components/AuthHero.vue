<template>
  <div class="auth-hero">
    <div class="hero-eyebrow">
      <lucide-icon name="cross" :size="14" :stroke-width="2.2" />
      <span>{{ $t('auth.eyebrow') }}</span>
      <span class="eyebrow-line"></span>
    </div>

    <h1 class="hero-title">
      <span class="title-solid">{{ $t('auth.titleA') }}</span>
      <span class="title-outline">{{ $t('auth.titleB') }}</span>
    </h1>

    <p class="hero-desc">{{ $t('auth.desc') }}</p>

    <div class="hero-chips">
      <div class="chip" v-for="(chip, i) in chips" :key="chip.key" :style="{ animationDelay: 0.55 + i * 0.12 + 's' }">
        <lucide-icon :name="chip.icon" :size="16" :stroke-width="1.8" />
        <span>{{ $t(chip.key) }}</span>
      </div>
    </div>

    <div class="hero-marquee">
      <div class="marquee-track">
        <span v-for="n in 2" :key="n" class="marquee-group">
          <span class="marquee-item" v-for="(chip, i) in marqueeItems" :key="i">
            {{ $t(chip) }}
            <lucide-icon name="plus" :size="11" :stroke-width="2.4" />
          </span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import LucideIcon from './LucideIcon.vue';

export default {
  name: 'AuthHero',
  components: { LucideIcon },
  data() {
    return {
      chips: [
        { key: 'auth.chipTriage', icon: 'activity' },
        { key: 'auth.chipDepartment', icon: 'stethoscope' },
        { key: 'auth.chipInsurance', icon: 'shield-check' },
        { key: 'auth.chipEducation', icon: 'heart-pulse' },
      ],
      marqueeItems: [
        'auth.chipTriage',
        'auth.chipDepartment',
        'auth.chipInsurance',
        'auth.chipEducation',
        'auth.marqueeVoice',
        'auth.marqueeKnowledge',
      ],
    };
  },
};
</script>

<style lang="scss" scoped>
.auth-hero {
  position: relative;
  z-index: 2;
  max-width: 620px;
  color: #eaf7f5;
  text-align: left;
  user-select: none;
}

.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #5eead4;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.42em;
  text-transform: uppercase;
  animation: rise-in 0.9s cubic-bezier(0.16, 1, 0.3, 1) both;

  .eyebrow-line {
    width: 72px;
    height: 1px;
    background: linear-gradient(90deg, rgba(94, 234, 212, 0.8), transparent);
  }
}

.hero-title {
  margin: 26px 0 0;
  line-height: 1.02;
  font-weight: 800;
  letter-spacing: 0.01em;

  span {
    display: block;
  }

  .title-solid {
    font-size: clamp(44px, 5.4vw, 84px);
    background: linear-gradient(105deg, #f4fffd 30%, #7df3e1 75%, #4f7cff 105%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rise-in 0.9s 0.12s cubic-bezier(0.16, 1, 0.3, 1) both;
  }

  .title-outline {
    margin-top: 6px;
    font-size: clamp(40px, 4.8vw, 74px);
    color: transparent;
    -webkit-text-stroke: 1.5px rgba(148, 214 , 233, 0.55);
    letter-spacing: 0.05em;
    animation: rise-in 0.9s 0.24s cubic-bezier(0.16, 1, 0.3, 1) both;
  }
}

.hero-desc {
  margin-top: 26px;
  max-width: 460px;
  font-size: 15px;
  line-height: 1.9;
  color: rgba(214, 233, 235, 0.72);
  animation: rise-in 0.9s 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 34px;

  .chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 16px;
    border: 1px solid rgba(94, 234, 212, 0.24);
    border-radius: 999px;
    background: rgba(9, 22, 33, 0.5);
    backdrop-filter: blur(8px);
    color: #bff5ec;
    font-size: 13px;
    letter-spacing: 0.08em;
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.35s, box-shadow 0.35s;
    animation: rise-in 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;

    &:hover {
      transform: translateY(-3px);
      border-color: rgba(94, 234, 212, 0.6);
      box-shadow: 0 12px 32px -14px rgba(45, 212, 191, 0.55);
    }
  }
}

.hero-marquee {
  margin-top: 52px;
  width: min(520px, 40vw);
  overflow: hidden;
  border-top: 1px solid rgba(148, 214, 233, 0.14);
  padding-top: 16px;
  mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent);

  .marquee-track {
    display: flex;
    width: max-content;
    animation: marquee 26s linear infinite;
  }

  .marquee-group {
    display: flex;
  }

  .marquee-item {
    display: inline-flex;
    align-items: center;
    gap: 14px;
    margin-right: 14px;
    white-space: nowrap;
    color: rgba(148, 214, 233, 0.4);
    font-size: 12px;
    letter-spacing: 0.34em;
    text-transform: uppercase;
  }
}

@keyframes marquee {
  to {
    transform: translateX(-50%);
  }
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(26px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-eyebrow,
  .hero-title span,
  .hero-desc,
  .hero-chips .chip {
    animation: none;
  }

  .marquee-track {
    animation: none;
  }
}
</style>
