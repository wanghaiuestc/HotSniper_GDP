#include "scheduler_manual.h"
#include "config.hpp"

SchedulerManual::SchedulerManual(ThreadManager *thread_manager)
   : SchedulerPinnedBase(thread_manager, SubsecondTime::NS(Sim()->getCfg()->getInt("scheduler/manual/quantum")))
   , core_index(0)
   , m_next_core(Sim()->getCfg()->getIntArray("scheduler/manual/core_order", 0))
{
  // Initiate core_order here
  
  // first, count the core order length in core_order_length
  int core_order_length = 0;
  while(Sim()->getCfg()->getIntArray("scheduler/manual/core_order", core_order_length) != -1)
    core_order_length++;
  if (core_order_length == 0)
    std::cout<<"Please provide the correct core_order in scheduler/manual/core_order of base.cfg"<<std::endl;

  // size the core_order vector and assign values
  core_order.resize(core_order_length);
  std::cout<<"[scheduler] [Manual]: "<< "Core order specified: ";
  for (int i = 0; i < core_order_length; i++)
    {
      core_order[i] = Sim()->getCfg()->getIntArray("scheduler/manual/core_order", i);
      std::cout<<core_order[i]<<" ";
    }
  std::cout<<std::endl;
}


void SchedulerManual::threadSetInitialAffinity(thread_id_t thread_id)
{
  // assign the thread to core
  m_thread_info[thread_id].setAffinitySingle(m_next_core);
  std::cout<<"[scheduler] [Manual]: "<<"Assigned thread "<<thread_id<<" to core "<<m_next_core<<std::endl;
  
  // find the next core in core order specified by the user,
  // core order will loop back (using mod operation) if there are more threads
  core_index++;
  m_next_core = core_order[core_index%(core_order.size())];
}
