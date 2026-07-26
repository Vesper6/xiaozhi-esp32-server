<template>
  <div class="auth-stage" @keyup.enter="login">
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

      <!-- 语言切换下拉菜单 -->
      <el-dropdown trigger="click" class="lang-switch" @visible-change="handleLanguageDropdownVisibleChange">
        <span class="el-dropdown-link">
          <lucide-icon name="globe" :size="15" :stroke-width="1.8" />
          <span>{{ currentLanguageText }}</span>
          <lucide-icon name="chevron-down" :size="14" :stroke-width="2"
            class="lang-caret" :class="{ 'rotate-down': languageDropdownVisible }" />
        </span>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item @click.native="changeLanguage('zh_CN')">
            {{ $t("language.zhCN") }}
          </el-dropdown-item>
          <el-dropdown-item @click.native="changeLanguage('zh_TW')">
            {{ $t("language.zhTW") }}
          </el-dropdown-item>
          <el-dropdown-item @click.native="changeLanguage('en')">
            {{ $t("language.en") }}
          </el-dropdown-item>
          <el-dropdown-item @click.native="changeLanguage('de')">
            {{ $t("language.de") }}
          </el-dropdown-item>
          <el-dropdown-item @click.native="changeLanguage('vi')">
            {{ $t("language.vi") }}
          </el-dropdown-item>
          <el-dropdown-item @click.native="changeLanguage('pt_BR')">
            {{ $t("language.ptBR") }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>

    <div class="auth-layout">
      <auth-hero />

      <div class="auth-card">
        <div class="card-head">
          <div class="card-title">
            <span class="title-icon">
              <lucide-icon name="log-in" :size="18" :stroke-width="2" />
            </span>
            {{ $t("login.title") }}
          </div>
          <div class="card-sub">{{ $t("login.welcome") }}</div>
        </div>

        <!-- 用户名登录 -->
        <template v-if="!isMobileLogin">
          <div class="field">
            <lucide-icon name="user" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-input v-model="form.username" :placeholder="$t('login.usernamePlaceholder')" />
          </div>
        </template>

        <!-- 手机号登录 -->
        <template v-else>
          <div class="field">
            <lucide-icon name="smartphone" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-select v-model="form.areaCode" style="width: 150px">
              <el-option v-for="item in mobileAreaList" :key="item.key" :label="`${item.name} (${item.key})`"
                :value="item.key" />
            </el-select>
            <el-input v-model="form.mobile" :placeholder="$t('login.mobilePlaceholder')" />
          </div>
        </template>

        <div class="field">
          <lucide-icon name="lock" :size="18" :stroke-width="1.8" class="field-icon" />
          <el-input v-model="form.password" :placeholder="$t('login.passwordPlaceholder')" type="password"
            show-password />
        </div>

        <div class="field-row">
          <div class="field">
            <lucide-icon name="shield-check" :size="18" :stroke-width="1.8" class="field-icon" />
            <el-input v-model="form.captcha" :placeholder="$t('login.captchaPlaceholder')" />
          </div>
          <img loading="lazy" v-if="captchaUrl" :src="captchaUrl" alt="captcha" class="captcha-img"
            @click="fetchCaptcha" />
        </div>

        <div class="auth-links">
          <div v-if="allowUserRegister" class="link" @click="goToRegister">
            <lucide-icon name="user-plus" :size="14" :stroke-width="2" />
            {{ $t("login.register") }}
          </div>
          <span v-else></span>
          <div class="link" @click="goToForgetPassword" v-if="enableMobileRegister">
            <lucide-icon name="key-round" :size="14" :stroke-width="2" />
            {{ $t("login.forgetPassword") }}
          </div>
        </div>

        <div class="auth-submit" @click="login">
          {{ $t("login.login") }}
          <lucide-icon name="arrow-right" :size="18" :stroke-width="2.2" class="submit-arrow" />
        </div>

        <!-- 登录方式切换按钮 -->
        <div class="login-type-switch" v-if="enableMobileRegister">
          <button type="button" class="type-btn" :class="{ active: isMobileLogin }"
            @click="switchLoginType('mobile')">
            <lucide-icon name="smartphone" :size="14" :stroke-width="2" />
            {{ $t("login.mobileLogin") }}
          </button>
          <button type="button" class="type-btn" :class="{ active: !isMobileLogin }"
            @click="switchLoginType('username')">
            <lucide-icon name="user" :size="14" :stroke-width="2" />
            {{ $t("login.usernameLogin") }}
          </button>
        </div>

        <div class="auth-meta">
          {{ $t("login.agreeTo") }}
          <div class="link" @click="openPage('/user-agreement.html')">
            {{ $t("login.userAgreement") }}
          </div>
          {{ $t("login.and") }}
          <div class="link" @click="openPage('/privacy-policy.html')">
            {{ $t("login.privacyPolicy") }}
          </div>
        </div>
      </div>
    </div>

    <div class="auth-footer">
      <version-footer />
    </div>
  </div>
</template>

<script>
import Api from "@/apis/api";
import AuthCanvas from "@/components/AuthCanvas.vue";
import AuthHero from "@/components/AuthHero.vue";
import LucideIcon from "@/components/LucideIcon.vue";
import VersionFooter from "@/components/VersionFooter.vue";
import i18n, { changeLanguage } from "@/i18n";
import { getUUID, goToPage, showDanger, showSuccess, sm2Encrypt, validateMobile } from "@/utils";
import { mapState } from "vuex";
import featureManager from "@/utils/featureManager";

export default {
  name: "login",
  components: {
    VersionFooter,
    AuthCanvas,
    AuthHero,
    LucideIcon,
  },
  computed: {
    ...mapState({
      allowUserRegister: (state) => state.pubConfig.allowUserRegister,
      enableMobileRegister: (state) => state.pubConfig.enableMobileRegister,
      mobileAreaList: (state) => state.pubConfig.mobileAreaList,
      sm2PublicKey: (state) => state.pubConfig.sm2PublicKey,
    }),
    // 获取当前语言
    currentLanguage() {
      return i18n.locale || "zh_CN";
    },
    // 获取当前语言显示文本
    currentLanguageText() {
      const currentLang = this.currentLanguage;
      switch (currentLang) {
        case "zh_CN":
          return this.$t("language.zhCN");
        case "zh_TW":
          return this.$t("language.zhTW");
        case "en":
          return this.$t("language.en");
        case "de":
          return this.$t("language.de");
        case "vi":
          return this.$t("language.vi");
        case "pt_BR":
          return this.$t("language.ptBR");
        default:
          return this.$t("language.zhCN");
      }
    },
  },
  data() {
    return {
      activeName: "username",
      form: {
        username: "",
        password: "",
        captcha: "",
        captchaId: "",
        areaCode: "+86",
        mobile: "",
      },
      captchaUuid: "",
      captchaUrl: "",
      isMobileLogin: false,
      languageDropdownVisible: false,
    };
  },
  mounted() {
    this.fetchCaptcha();
    this.$store.dispatch("fetchPubConfig").then(() => {
      // 根据配置决定默认登录方式
      this.isMobileLogin = this.enableMobileRegister;
    });
  },
  methods: {
    openPage(url) {
      const lang = this.$i18n ? this.$i18n.locale : 'zh_CN';
      if (!lang.startsWith('zh')) {
        url = url.replace('.html', '-en.html');
      }
      window.open(url, '_blank');
    },
    fetchCaptcha() {
      // 处理手动清空localstorage导致无法获取验证码的问题
      const token = localStorage.getItem('token')
      if (token) {
        if (this.$route.path !== "/home") {
          this.$router.push("/home");
        }
      } else {
        this.captchaUuid = getUUID();

        Api.user.getCaptcha(this.captchaUuid, (res) => {
          if (res.status === 200) {
            const blob = new Blob([res.data], { type: res.data.type });
            this.captchaUrl = URL.createObjectURL(blob);
          } else {
            showDanger("验证码加载失败，点击刷新");
          }
        });
      }
    },

    // 切换语言下拉菜单的可见状态变化
    handleLanguageDropdownVisibleChange(visible) {
      this.languageDropdownVisible = visible;
    },

    // 切换语言
    changeLanguage(lang) {
      changeLanguage(lang);
      this.languageDropdownVisible = false;
      this.$message.success({
        message: this.$t("message.success"),
        showClose: true,
      });
    },

    // 切换登录方式
    switchLoginType(type) {
      this.isMobileLogin = type === "mobile";
      // 清空表单
      this.form.username = "";
      this.form.mobile = "";
      this.form.password = "";
      this.form.captcha = "";
      this.fetchCaptcha();
    },

    // 封装输入验证逻辑
    validateInput(input, messageKey) {
      if (!input.trim()) {
        showDanger(this.$t(messageKey));
        return false;
      }
      return true;
    },
    
    getUserInfo() {
      Api.user.getUserInfo(({ data }) => {
        if (data.code === 0) {
          this.$store.commit("setUserInfo", data.data);
          goToPage("/home");
        } else {
          showDanger("用户信息获取失败");
        }
      });
    },

    async login() {
      if (this.isMobileLogin) {
        // 手机号登录验证
        if (!validateMobile(this.form.mobile, this.form.areaCode)) {
          showDanger(this.$t('login.requiredMobile'));
          return;
        }
        // 拼接手机号作为用户名
        this.form.username = this.form.areaCode + this.form.mobile;
      } else {
        // 用户名登录验证
        if (!this.validateInput(this.form.username, 'login.requiredUsername')) {
          return;
        }
      }

      // 验证密码
      if (!this.validateInput(this.form.password, 'login.requiredPassword')) {
        return;
      }
      // 验证验证码
      if (!this.validateInput(this.form.captcha, 'login.requiredCaptcha')) {
        return;
      }
      // 加密密码
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

      const plainUsername = this.form.username;

      this.form.captchaId = this.captchaUuid;

      // 加密
      const loginData = {
        username: plainUsername,
        password: encryptedPassword,
        captchaId: this.form.captchaId
      };

      Api.user.login(
        loginData,
        ({ data }) => {
          showSuccess(this.$t('login.loginSuccess'));
          this.$store.commit("setToken", JSON.stringify(data.data));
          this.getUserInfo();
        },
        (err) => {
          // 直接使用后端返回的国际化消息
          let errorMessage = err.data.msg || "登录失败";

          showDanger(errorMessage);
        }
      );

      // 重新获取验证码
      setTimeout(() => {
        this.fetchCaptcha();
      }, 1000);
    },

    goToRegister() {
      goToPage("/register");
    },
    goToForgetPassword() {
      goToPage("/retrieve-password");
    }
  },
};
</script>
<style lang="scss" scoped>
@import "./auth.scss";
</style>
