#ifndef __SCHEDULER_MANUAL_H
#define __SCHEDULER_MANUAL_H

#include "scheduler_pinned_base.h"

class SchedulerManual : public SchedulerPinnedBase
{
   public:
      SchedulerManual(ThreadManager *thread_manager);

      virtual void threadSetInitialAffinity(thread_id_t thread_id);

   private:
      std::vector<int> core_order;

      int core_index;

      core_id_t m_next_core;
};

#endif
