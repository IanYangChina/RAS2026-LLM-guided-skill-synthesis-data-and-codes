## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 9 | 0.0641 | 0.01 | ❌ rejected |
| 1 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 8 | 0.2346 | 0.18 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.064) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.064
- **task_score** (E): 0.005
- **fitness_score**: 0.204  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1751 |
| align_contact | 1.00 | 1.00 | 0.1026 |
| grasp_peg | 1.00 | 1.00 | 0.0000 |
| push_insert | 1.00 | 1.00 | 0.0011 |
| retract | 0.33 | 1.00 | 0.1055 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.092, 0.164) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| align_contact | contact | 1.00 / force_exceeded | (0.516, 0.092, 0.164)→(0.504, 0.086, 0.063) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 25.828 | 25.828 |
| grasp_peg | grasp | 1.00 / step_budget | (0.503, 0.085, 0.060)→(0.503, 0.085, 0.060) | (0.505, 0.084, 0.034)→(0.503, 0.084, 0.032) | 0.164→0.164 | 1.00 / 2.000 | 50.021 | 60.470 |
| push_insert | insert | 1.00 / force_exceeded | (0.503, 0.085, 0.060)→(0.503, 0.085, 0.060) | (0.503, 0.084, 0.032)→(0.504, 0.083, 0.032) | 0.164→0.164 | 1.00 / 2.000 | 188.042 | 188.042 |
| retract | retract | 0.33 / step_budget | (0.503, 0.085, 0.060)→(0.500, 0.084, 0.166) | (0.504, 0.083, 0.032)→(0.503, 0.083, 0.034) | 0.164→0.163 | 1.00 / 1.000 | 0.548 | 38.874 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.010
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.010
- phase_score: 0.362
- phase_breakdown.insertion_depth_score: 0.003
- phase_breakdown.contact_peg_score: 0.654
- phase_breakdown.reach_above_peg_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.221
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.010
- **Median Q (composite search score)**: 0.062
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: align_contact.contact_force
- **Final σ (mean)**: 0.278


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02809,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force":19.58842,"align_contact.contact_speed":0.02581,"approach_peg.approach_speed":0.07757,"approach_peg.approach_tolerance":0.01774,"push_insert.push_distance":0.1745,"push_insert.push_force":19.11727,"push_insert.push_speed":0.04204,"retract.retract_speed":0.05254,"retract.retract_tolerance":0.01016},"optimized_scores":{"best_composite_score":0.04925,"best_fitness_score":0.18925,"best_task_score":0.00169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51501,0.08272,0.00883],"force_p95":161.93054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.79093,"mean_force":91.18698,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.50711,0.08178,0.0604]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51812,0.08189,0.05667],"force_p95":160.28465,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.0885,"mean_force":90.05002,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.50711,0.08178,0.0604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.51676,0.08185,0.00888],"force_p95":59.67295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.3752,"mean_force":50.8132,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50706,0.08191,0.06061]},{"body_a":"attachment","body_b":"peg","contact_count":550.0,"contact_point_centroid":[0.51808,0.08194,0.05681],"force_p95":59.16454,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.87123,"mean_force":50.3117,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50706,0.08191,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50402,0.07946,0.00938],"force_p95":0.55941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.97619,"mean_force":0.90925,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50441,0.08064,0.1065]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.51803,0.08155,0.05784],"force_p95":20.71763,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.63593,"mean_force":9.20617,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50703,0.08118,0.06202]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.50598,0.08088,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.29984,"mean_force":0.61986,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.51831,0.08503,0.11295]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5195,0.08223,0.05867],"force_p95":20.65674,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.86908,"mean_force":18.74577,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.50846,0.08221,0.06328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.5057,0.08086,0.00936],"force_p95":0.55706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57224,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51469,0.14173,0.22744]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49998,0.19757,0.29666]}],"total_contact_groups":10},"final_pose_error":0.05802,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50415,0.0799,0.03384],"final_tcp_position":[0.50452,0.08064,0.15235],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":169.79093,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":635.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.53004,0.0882,0.16375],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08088,0.03376],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":21.29984,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":512.0,"raw_peak_contact_force":21.29984,"subtask_id":"contact_peg","tcp_end":[0.50843,0.08219,0.06301],"tcp_start":[0.53004,0.0882,0.16375],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50486,0.08058,0.03267],"object_pos_start":[0.50596,0.08088,0.03376],"object_to_goal_dist_end":0.16082,"object_to_goal_dist_start":0.16111,"object_z_max":0.03376,"peak_contact_force":56.46372,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1100.0,"raw_peak_contact_force":61.3752,"subtask_id":"contact_peg","tcp_end":[0.50699,0.08191,0.06044],"tcp_start":[0.50698,0.08189,0.0604],"tcp_to_object_dist_end":0.02788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5052,0.08022,0.03281],"object_pos_start":[0.50481,0.08059,0.03276],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.16082,"object_z_max":0.03276,"peak_contact_force":169.79093,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":169.79093,"subtask_id":"insertion_depth","tcp_end":[0.50777,0.08117,0.06028],"tcp_start":[0.50699,0.08191,0.06044],"tcp_to_object_dist_end":0.02761,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50415,0.0799,0.03384],"object_pos_start":[0.5052,0.08022,0.03281],"object_to_goal_dist_end":0.16007,"object_to_goal_dist_start":0.16046,"object_z_max":0.03445,"peak_contact_force":0.54553,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":40.97619,"tcp_end":[0.50452,0.08064,0.15235],"tcp_start":[0.50777,0.08117,0.06028],"tcp_to_object_dist_end":0.11852,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15432,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force":14.65696,"align_contact.contact_speed":0.02506,"approach_peg.approach_speed":0.10036,"approach_peg.approach_tolerance":0.01277,"push_insert.push_distance":0.10901,"push_insert.push_force":17.21655,"push_insert.push_speed":0.03425,"retract.retract_speed":0.07825,"retract.retract_tolerance":0.01329},"optimized_scores":{"best_composite_score":0.06211,"best_fitness_score":0.20211,"best_task_score":0.00455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.5126,0.106,0.00867],"force_p95":180.66675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.4581,"mean_force":101.54457,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.50405,0.10505,0.06022]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51507,0.10525,0.05643],"force_p95":179.22216,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.95998,"mean_force":100.58181,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.50405,0.10505,0.06022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.51378,0.10491,0.00878],"force_p95":54.74472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.97909,"mean_force":48.35101,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50404,0.10519,0.06051]},{"body_a":"attachment","body_b":"peg","contact_count":550.0,"contact_point_centroid":[0.51506,0.10536,0.05666],"force_p95":54.24451,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.47829,"mean_force":47.84671,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50404,0.10519,0.06051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50432,0.10286,0.00938],"force_p95":0.56937,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.29801,"mean_force":0.83292,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50148,0.10384,0.12337]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.51503,0.10496,0.05759],"force_p95":16.56555,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.88613,"mean_force":8.32323,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50403,0.10451,0.0618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50596,0.10454,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.97185,"mean_force":0.58242,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.51148,0.10818,0.11354]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5167,0.10586,0.05878],"force_p95":19.4955,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.4955,"mean_force":19.4955,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.50566,0.10559,0.06339]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.5056,0.10471,0.00937],"force_p95":0.57748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56875,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50925,0.15383,0.22858]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19792,0.29672]}],"total_contact_groups":10},"final_pose_error":0.02279,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5044,0.1031,0.03387],"final_tcp_position":[0.5018,0.10389,0.1875],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":189.4581,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5424,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51953,0.11127,0.16538],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10458,0.03383],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":19.97185,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":539.0,"raw_peak_contact_force":19.97185,"subtask_id":"contact_peg","tcp_end":[0.50565,0.10559,0.06322],"tcp_start":[0.51953,0.11127,0.16538],"tcp_to_object_dist_end":0.02941,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50467,0.10395,0.03245],"object_pos_start":[0.50584,0.10458,0.03383],"object_to_goal_dist_end":0.18417,"object_to_goal_dist_start":0.18477,"object_z_max":0.03392,"peak_contact_force":53.226,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1100.0,"raw_peak_contact_force":55.97909,"subtask_id":"contact_peg","tcp_end":[0.50392,0.10518,0.06026],"tcp_start":[0.50392,0.10516,0.06026],"tcp_to_object_dist_end":0.02785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50507,0.10352,0.03245],"object_pos_start":[0.50467,0.10386,0.03244],"object_to_goal_dist_end":0.18374,"object_to_goal_dist_start":0.18408,"object_z_max":0.03244,"peak_contact_force":189.4581,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":189.4581,"subtask_id":"insertion_depth","tcp_end":[0.50473,0.10449,0.0601],"tcp_start":[0.50392,0.10518,0.06026],"tcp_to_object_dist_end":0.02766,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5044,0.1031,0.03387],"object_pos_start":[0.50507,0.10352,0.03245],"object_to_goal_dist_end":0.18325,"object_to_goal_dist_start":0.18374,"object_z_max":0.03434,"peak_contact_force":0.54851,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1035.0,"raw_peak_contact_force":38.29801,"tcp_end":[0.5018,0.10389,0.1875],"tcp_start":[0.50473,0.10449,0.0601],"tcp_to_object_dist_end":0.15365,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84181,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force":29.99936,"align_contact.contact_speed":0.01706,"approach_peg.approach_speed":0.10441,"approach_peg.approach_tolerance":0.00965,"push_insert.push_distance":0.12289,"push_insert.push_force":23.87115,"push_insert.push_speed":0.02179,"retract.retract_speed":0.05471,"retract.retract_tolerance":0.01091},"optimized_scores":{"best_composite_score":0.08094,"best_fitness_score":0.22094,"best_task_score":0.00956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50807,0.06904,0.00848],"force_p95":195.57496,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.87626,"mean_force":111.86328,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.49675,0.06865,0.06015]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50764,0.06888,0.05607],"force_p95":194.41369,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.66654,"mean_force":111.13805,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.49675,0.06865,0.06015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50514,0.06797,0.00859],"force_p95":63.33718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.05459,"mean_force":49.19063,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49674,0.06882,0.06041]},{"body_a":"attachment","body_b":"peg","contact_count":550.0,"contact_point_centroid":[0.50762,0.06895,0.05628],"force_p95":62.82831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.52214,"mean_force":48.68734,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49674,0.06882,0.06041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49934,0.06562,0.00937],"force_p95":0.58741,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.34836,"mean_force":0.98709,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49406,0.06759,0.10866]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.50736,0.06852,0.0576],"force_p95":20.73475,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.7565,"mean_force":9.89632,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4965,0.06811,0.06208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50311,0.06746,0.00938],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.21321,"mean_force":0.74372,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.49776,0.07219,0.11212]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50922,0.06926,0.05859],"force_p95":33.52526,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.76928,"mean_force":24.60416,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.4983,0.06913,0.06338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":593.0,"contact_point_centroid":[0.50302,0.06743,0.00934],"force_p95":0.55519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56115,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4991,0.13655,0.22913]}],"total_contact_groups":9},"final_pose_error":0.05315,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49978,0.06593,0.03379],"final_tcp_position":[0.49423,0.06759,0.157],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":204.87626,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54593,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":593.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_above_peg","tcp_end":[0.49986,0.0757,0.16427],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":622.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06742,0.03375],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":36.21321,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":627.0,"raw_peak_contact_force":36.21321,"subtask_id":"contact_peg","tcp_end":[0.49837,0.06912,0.063],"tcp_start":[0.49986,0.0757,0.16427],"tcp_to_object_dist_end":0.02967,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50048,0.06696,0.03208],"object_pos_start":[0.50303,0.06742,0.03375],"object_to_goal_dist_end":0.14717,"object_to_goal_dist_start":0.14758,"object_z_max":0.03375,"peak_contact_force":40.37448,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1100.0,"raw_peak_contact_force":64.05459,"subtask_id":"contact_peg","tcp_end":[0.49663,0.0688,0.06019],"tcp_start":[0.49661,0.06879,0.06018],"tcp_to_object_dist_end":0.02844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50063,0.06643,0.03205],"object_pos_start":[0.50026,0.06681,0.03208],"object_to_goal_dist_end":0.14664,"object_to_goal_dist_start":0.14703,"object_z_max":0.03208,"peak_contact_force":204.87626,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":204.87626,"subtask_id":"insertion_depth","tcp_end":[0.49738,0.06804,0.06005],"tcp_start":[0.49663,0.0688,0.06019],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49978,0.06593,0.03379],"object_pos_start":[0.50063,0.06643,0.03205],"object_to_goal_dist_end":0.14606,"object_to_goal_dist_start":0.14664,"object_z_max":0.03457,"peak_contact_force":0.54953,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1045.0,"raw_peak_contact_force":37.34836,"tcp_end":[0.49423,0.06759,0.157],"tcp_start":[0.49738,0.06804,0.06005],"tcp_to_object_dist_end":0.12334,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```