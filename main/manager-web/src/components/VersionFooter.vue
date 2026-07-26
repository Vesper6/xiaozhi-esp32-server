<template>
  <div class="copyright">
    <div class="footer-content">
      <span>{{ year }} {{ name }} {{ version }}</span>
      <template v-if="beianGaNum !== 'null'">
        <span v-if="beianIcpNum !== 'null' || name">|</span>
        <a :href="'http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=' + beianGaNum" target="_blank"
          rel="noopener" class="beian-link">
          <lucide-icon name="shield-check" :size="13" :stroke-width="2" class="beian-icon" />
          <span class="beian-text">{{ beianGaNum }}</span>
        </a>
      </template>
      <template v-if="beianIcpNum !== 'null'">
        <span v-if="name">|</span>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" class="beian-link">
          <span class="beian-text">{{ beianIcpNum }}</span>
        </a>
      </template>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import LucideIcon from '@/components/LucideIcon.vue';

export default {
  name: 'VersionFooter',
  components: { LucideIcon },
  computed: {
    ...mapState({
      version: state => state.pubConfig.version,
      name: state => state.pubConfig.name,
      beianIcpNum: state => state.pubConfig.beianIcpNum,
      beianGaNum: state => state.pubConfig.beianGaNum,
      year: state => state.pubConfig.year
    })
  },
  mounted() {
    this.$store.dispatch('fetchPubConfig')
  }
}
</script>

<style scoped>
.copyright {
  padding: 10px 0;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.beian-link {
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.beian-icon {
  margin-right: 4px;
  color: inherit;
  vertical-align: middle;
}

.beian-text {
  color: inherit;
  font-size: 12px;
  vertical-align: middle;
}
</style>