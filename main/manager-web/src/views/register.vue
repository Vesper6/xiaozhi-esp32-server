<template>
  <div class="auth-stage" @keyup.enter="register">
    <auth-canvas />

    <div class="auth-topbar">
      <div class="brand">
        <div class="brand-mark">
          <lucide-icon name="cross" :size="20" :stroke-width="2.2" />
        </div>
        <div>
          <div class="brand-name">{{ $t("auth.brand") }}</div>
          <div class="brand-sub">AI Medical Triage</div>
        </div>
      </div>
    </div>

    <div class="auth-layout">
      <auth-hero />

      <div class="auth-card">
        <div class="card-head">
          <div class="card-title">
            <span class="title-icon">
              <lucide-icon name="user-plus" :size="18" :stroke-width="2" />
            </span>
            {{ $t('register.title') }}
          </div>
          <div class="card-sub">{{ $t('register.welcome') }}</div>
        </div>

        <form @submit.prevent="register">
          <!-- 用户名注册 -->
          <div class="field" v-if="!enableMobileRegister">
            <lucide-icon name="user" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-input v-model="form.username" :placeholder="$t('register.usernamePlaceholder')" />
          </div>

          <!-- 手机号注册部分 -->
          <template v-if="enableMobileRegister">
            <div class="field">
              <lucide-icon name="smartphone" :size="18" :stroke-width="1.8" class="field-icon" />
              <el-select v-model="form.areaCode" style="width: 150px">
                <el-option v-for="item in mobileAreaList" :key="item.key" :label="`${item.name} (${item.key})`"
                  :value="item.key" />
              </el-select>
              <el-input v-model="form.mobile" :placeholder="$t('register.mobilePlaceholder')" />
            </div>

            <div class="field-row">
              <div class="field">
                <lucide-icon name="shield-check" :size="18" :stroke-width="1.8" class="field-icon" />
                <el-input v-model="form.captcha" :placeholder="$t('register.captchaPlaceholder')" />
              </div>
              <img loading="lazy" v-if="captchaUrl" :src="captchaUrl" alt="captcha" class="captcha-img"
                @click="fetchCaptcha" />
            </div>

            <!-- 手机验证码 -->
            <div class="field-row">
              <div class="field">
                <lucide-icon name="smartphone" :size="18" :stroke-width="1.8" class="field-icon" />
                <el-input v-model="form.mobileCaptcha" :placeholder="$t('register.mobileCaptchaPlaceholder')"
                  maxlength="6" />
              </div>
              <el-button class="send-captcha-btn" :disabled="!canSendMobileCaptcha" @click="sendMobileCaptcha">
                <span>
                  {{ countdown > 0 ? `${countdown}${$t('register.secondsLater')}` : $t('register.sendCaptcha') }}
                </span>
              </el-button>
            </div>
          </template>

          <!-- 密码输入框 -->
          <div class="field">
            <lucide-icon name="lock" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-input v-model="form.password" :placeholder="$t('register.passwordPlaceholder')" type="password"
              show-password />
          </div>

          <!-- 确认密码 -->
          <div class="field">
            <lucide-icon name="lock" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-input v-model="form.confirmPassword" :placeholder="$t('register.confirmPasswordPlaceholder')"
              type="password" show-password />
          </div>

          <!-- 用户名注册时的图形验证码 -->
          <div v-if="!enableMobileRegister" class="field-row">
            <div class="field">
              <lucide-icon name="shield-check" :size="18" :stroke-width="1.8" class="field-icon" />
              <el-input v-model="form.captcha" :placeholder="$t('register.captchaPlaceholder')" />
            </div>
            <img loading="lazy" v-if="captchaUrl" :src="captchaUrl" alt="captcha" class="captcha-img"
              @click="fetchCaptcha" />
          </div>

          <div class="auth-links">
            <div class="link" @click="goToLogin">
              <lucide-icon name="log-in" :size="14" :stroke-width="2" />
              {{ $t('register.goToLogin') }}
            </div>
          </div>
        </form>

        <div class="auth-submit" @click="register">
          {{ $t('register.registerButton') }}
          <lucide-icon name="arrow-right" :size="18" :stroke-width="2.2" class="submit-arrow" />
        </div>

        <div class="auth-meta">
          {{ $t('register.agreeTo') }}
          <div class="link" @click="openPage('/user-agreement.html')">{{ $t('register.userAgreement') }}</div>
          {{ $t('login.and') }}
          <div class="link" @click="openPage('/privacy-policy.html')">{{ $t('register.privacyPolicy') }}</div>
        </div>
      </div>
    </div>

    <div class="auth-footer">
      <version-footer />
    </div>
  </div>
</template>

<script>
import Api from '@/apis/api';
import AuthCanvas from '@/components/AuthCanvas.vue';
import AuthHero from '@/components/AuthHero.vue';
import LucideIcon from '@/components/LucideIcon.vue';
import VersionFooter from '@/components/VersionFooter.vue';
import { getUUID, goToPage, showDanger, showSuccess, sm2Encrypt, validateMobile } from '@/utils';
import { mapState } from 'vuex';
import i18n from '@/i18n';

export default {
  name: 'register',
  components: {
    VersionFooter,
    AuthCanvas,
    AuthHero,
    LucideIcon
  },
  computed: {
    ...mapState({
      allowUserRegister: state => state.pubConfig.allowUserRegister,
      enableMobileRegister: state => state.pubConfig.enableMobileRegister,
      mobileAreaList: state => state.pubConfig.mobileAreaList,
      sm2PublicKey: state => state.pubConfig.sm2PublicKey,
    }),
    // 获取当前语言
    currentLanguage() {
      return i18n.locale || "zh_CN";
    },
    canSendMobileCaptcha() {
      return this.countdown === 0 && validateMobile(this.form.mobile, this.form.areaCode);
    }
  },
  data() {
    return {
      form: {
        username: '',
        password: '',
        confirmPassword: '',
        captcha: '',
        captchaId: '',
        areaCode: '+86',
        mobile: '',
        mobileCaptcha: ''
      },
      captchaUrl: '',
      countdown: 0,
      timer: null,
    }
  },
  mounted() {
    this.$store.dispatch('fetchPubConfig').then(() => {
      if (!this.allowUserRegister) {
        showDanger(this.$t('register.notAllowRegister'));
        setTimeout(() => {
          goToPage('/login');
        }, 1500);
      }
    });
    this.fetchCaptcha();
  },
  methods: {
    openPage(url) {
      const lang = this.$i18n ? this.$i18n.locale : 'zh_CN';
      if (!lang.startsWith('zh')) {
        url = url.replace('.html', '-en.html');
      }
      window.open(url, '_blank');
    },
    // 复用验证码获取方法
    fetchCaptcha() {
      this.form.captchaId = getUUID();
      Api.user.getCaptcha(this.form.captchaId, (res) => {
        if (res.status === 200) {
          const blob = new Blob([res.data], { type: res.data.type });
          this.captchaUrl = URL.createObjectURL(blob);

        } else {
          console.error('验证码加载异常:', error);
          showDanger(this.$t('register.captchaLoadFailed'));
        }
      });
    },

    // 封装输入验证逻辑
    validateInput(input, message) {
      if (!input.trim()) {
        showDanger(message);
        return false;
      }
      return true;
    },

    // 发送手机验证码
    sendMobileCaptcha() {
      if (!validateMobile(this.form.mobile, this.form.areaCode)) {
        showDanger(this.$t('register.inputCorrectMobile'));
        return;
      }

      // 验证图形验证码
      if (!this.validateInput(this.form.captcha, this.$t('register.inputCaptcha'))) {
        this.fetchCaptcha();
        return;
      }

      // 清除可能存在的旧定时器
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }

      // 开始倒计时
      this.countdown = 60;
      this.timer = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--;
        } else {
          clearInterval(this.timer);
          this.timer = null;
        }
      }, 1000);

      // 调用发送验证码接口
      Api.user.sendSmsVerification({
        phone: this.form.areaCode + this.form.mobile,
        captcha: this.form.captcha,
        captchaId: this.form.captchaId
      }, (res) => {
        showSuccess(this.$t('register.captchaSendSuccess'));
      }, (err) => {
        showDanger(err.data.msg || this.$t('register.captchaSendFailed'));
        this.countdown = 0;
        this.fetchCaptcha();
      });
    },

    // 注册逻辑
    async register() {
      if (this.enableMobileRegister) {
        // 手机号注册验证
        if (!validateMobile(this.form.mobile, this.form.areaCode)) {
          showDanger(this.$t('register.inputCorrectMobile'));
          return;
        }
        if (!this.form.mobileCaptcha) {
          showDanger(this.$t('register.requiredMobileCaptcha'));
          return;
        }
      } else {
        // 用户名注册验证
        if (!this.validateInput(this.form.username, this.$t('register.requiredUsername'))) {
          return;
        }
      }

      // 验证密码
      if (!this.validateInput(this.form.password, this.$t('register.requiredPassword'))) {
        return;
      }
      if (this.form.password !== this.form.confirmPassword) {
        showDanger(this.$t('register.passwordsNotMatch'))
        return
      }
      // 验证验证码
      if (!this.validateInput(this.form.captcha, this.$t('register.requiredCaptcha'))) {
        return;
      }
      // 加密
      let encryptedPassword;
      try {
        // 拼接验证码和密码
        const captchaAndPassword = this.form.captcha + this.form.password;
        encryptedPassword = sm2Encrypt(this.sm2PublicKey, captchaAndPassword);
      } catch (error) {
        console.error("密码加密失败:", error);
        showDanger(this.$t('sm2.encryptionFailed'));
        return;
      }

      let plainUsername;
      if (this.enableMobileRegister) {
        plainUsername = this.form.areaCode + this.form.mobile;
      } else {
        plainUsername = this.form.username;
      }

      // 准备注册数据
      const registerData = {
        username: plainUsername,
        password: encryptedPassword,
        captchaId: this.form.captchaId,
        mobileCaptcha: this.form.mobileCaptcha
      };

      Api.user.register(registerData, ({ data }) => {
        showSuccess(this.$t('register.registerSuccess'))
        goToPage('/login')
      }, (err) => {
        showDanger(err.data.msg || this.$t('register.registerFailed'))
        if (err.data != null && err.data.msg != null && err.data.msg.indexOf('图形验证码') > -1) {
          this.fetchCaptcha()
        }
      })
    },

    goToLogin() {
      goToPage('/login')
    }
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }
}
</script>

<style lang="scss" scoped>
@import './auth.scss';
</style>
