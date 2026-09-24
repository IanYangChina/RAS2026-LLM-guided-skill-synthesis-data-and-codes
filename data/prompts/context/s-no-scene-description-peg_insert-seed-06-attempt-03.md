## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | 0.0817 | 0.87 | ❌ rejected |
| 2 | align → approach → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.0846 | 0.79 | ❌ rejected |
| 1 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | 0.0832 | 0.87 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0178 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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

## Current Skill (Q=0.082) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_socket
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_peg
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_socket
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_socket
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - -0.005
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_peg
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_peg
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.082
- **task_score** (E): 0.869
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1149 |
| approach_1 | 1.00 | 0.00 | 0.0599 |
| descend_1 | 0.00 | 0.00 | 0.0514 |
| insert_1 | 0.67 | 1.00 | 0.0295 |
| grasp_1 | 1.00 | 1.00 | 0.0008 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.016, 0.189) | (0.504, -0.000, 0.340)→(0.501, 0.016, 0.229) | 0.260→0.151 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.016, 0.189)→(0.497, 0.019, 0.129) | (0.501, 0.016, 0.229)→(0.498, 0.019, 0.169) | 0.151→0.094 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 0.00 / step_budget | (0.497, 0.019, 0.129)→(0.496, 0.019, 0.078) | (0.498, 0.019, 0.169)→(0.497, 0.019, 0.118) | 0.094→0.049 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.67 / step_budget | (0.496, 0.019, 0.078)→(0.501, 0.019, 0.050) | (0.497, 0.019, 0.118)→(0.501, 0.019, 0.090) | 0.049→0.030 | 1.00 / 1.000 | 303.720 | 333.270 |
| grasp_1 | grasp | 1.00 / step_budget | (0.501, 0.019, 0.050)→(0.502, 0.019, 0.050) | (0.501, 0.019, 0.090)→(0.501, 0.019, 0.090) | 0.030→0.030 | 1.00 / 1.000 | 64.518 | 96.730 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.944
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.944
- phase_score: 0.655
- phase_breakdown.reach_socket_score: 0.784
- phase_breakdown.insert_peg_score: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.770
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.944
- **Median Q (composite search score)**: 0.035
- **K-run variance**: 0.0116
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.296


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60385b1f31aca3065ea31945cfeaa028cd4432c7d54684f37d7ce3abfb247b97`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4bee8669cc79b9d5e3314636941bfd5dcacadb9648a0bfff5f763dbb49e79a76`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.55491,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00883,"align_1.lateral_offset_y":0.0033,"approach_1.approach_height":0.03699,"approach_1.approach_speed":0.03734,"descend_1.descend_force_threshold":24.44487,"descend_1.descend_speed":0.01512,"grasp_1.grasp_duration":1.80786,"insert_1.insert_distance":0.03874,"insert_1.insert_speed":0.02052},"optimized_scores":{"best_composite_score":0.23032,"best_fitness_score":0.77032,"best_task_score":0.94381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51331,-0.01241,0.04997],"force_p95":135.19276,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.19276,"mean_force":135.19276,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49831,-0.01246,0.05014]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.51368,-0.01235,0.04997],"force_p95":95.15453,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.59447,"mean_force":72.26093,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49868,-0.01248,0.05011]}],"total_contact_groups":2},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49835,-0.01246,0.04992],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":135.19276,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":352.0,"n_steps_budget":780.0,"object_pos_end":[0.50813,-0.00816,0.22884],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14929,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50766,-0.00816,0.18885],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.50167,-0.01164,0.16653],"object_pos_start":[0.50813,-0.00816,0.22884],"object_to_goal_dist_end":0.08732,"object_to_goal_dist_start":0.14929,"object_z_max":0.22884,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50075,-0.01163,0.12654],"tcp_start":[0.50766,-0.00816,0.18885],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50038,-0.01239,0.11786],"object_pos_start":[0.50167,-0.01164,0.16653],"object_to_goal_dist_end":0.03983,"object_to_goal_dist_start":0.08732,"object_z_max":0.16653,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.499,-0.01238,0.07788],"tcp_start":[0.50075,-0.01163,0.12654],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.49889,-0.01246,0.08992],"object_pos_start":[0.50038,-0.01239,0.11786],"object_to_goal_dist_end":0.01597,"object_to_goal_dist_start":0.03983,"object_z_max":0.11786,"peak_contact_force":135.19276,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":135.19276,"subtask_id":"insert_peg","tcp_end":[0.49835,-0.01246,0.04992],"tcp_start":[0.499,-0.01238,0.07788],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49933,-0.01249,0.09014],"object_pos_start":[0.49889,-0.01246,0.08992],"object_to_goal_dist_end":0.0161,"object_to_goal_dist_start":0.01597,"object_z_max":0.09015,"peak_contact_force":64.39162,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":103.59447,"tcp_end":[0.49888,-0.01249,0.05014],"tcp_start":[0.49835,-0.01246,0.04992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.30698,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00221,"align_1.lateral_offset_y":-0.00034,"approach_1.approach_height":0.03754,"approach_1.approach_speed":0.02077,"descend_1.descend_force_threshold":17.68852,"descend_1.descend_speed":0.01337,"grasp_1.grasp_duration":1.57581,"insert_1.insert_distance":0.03947,"insert_1.insert_speed":0.01977},"optimized_scores":{"best_composite_score":0.03519,"best_fitness_score":0.57519,"best_task_score":0.85569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.52016,0.03219,0.04976],"force_p95":348.07903,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.84807,"mean_force":270.07556,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50519,0.03139,0.04973]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.52128,0.03248,0.04996],"force_p95":101.32108,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.07619,"mean_force":72.49509,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50633,0.03144,0.05007]}],"total_contact_groups":2},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50542,0.03141,0.0493],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":355.84807,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":371.0,"n_steps_budget":810.0,"object_pos_end":[0.5085,0.02789,0.22808],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15092,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50804,0.02786,0.18808],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.50728,0.03083,0.16677],"object_pos_start":[0.5085,0.02789,0.22808],"object_to_goal_dist_end":0.09238,"object_to_goal_dist_start":0.15092,"object_z_max":0.22808,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50636,0.03078,0.12679],"tcp_start":[0.50804,0.02786,0.18808],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50713,0.03145,0.11755],"object_pos_start":[0.50728,0.03083,0.16677],"object_to_goal_dist_end":0.04949,"object_to_goal_dist_start":0.09238,"object_z_max":0.16677,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.50575,0.03137,0.07757],"tcp_start":[0.50636,0.03078,0.12679],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.03145,0.0893],"object_pos_start":[0.50713,0.03145,0.11755],"object_to_goal_dist_end":0.03332,"object_to_goal_dist_start":0.04949,"object_z_max":0.11755,"peak_contact_force":355.84807,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":355.84807,"subtask_id":"insert_peg","tcp_end":[0.50542,0.03141,0.0493],"tcp_start":[0.50575,0.03137,0.07757],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50688,0.03147,0.0901],"object_pos_start":[0.50593,0.03145,0.0893],"object_to_goal_dist_end":0.03376,"object_to_goal_dist_start":0.03332,"object_z_max":0.09011,"peak_contact_force":63.87929,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":111.07619,"tcp_end":[0.50653,0.03144,0.05011],"tcp_start":[0.50542,0.03141,0.0493],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.60513,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00072,"align_1.lateral_offset_y":-0.00577,"approach_1.approach_height":0.04504,"approach_1.approach_speed":0.03329,"descend_1.descend_force_threshold":16.03449,"descend_1.descend_speed":0.02953,"grasp_1.grasp_duration":1.76795,"insert_1.insert_distance":0.07997,"insert_1.insert_speed":0.01383},"optimized_scores":{"best_composite_score":-0.02029,"best_fitness_score":0.51971,"best_task_score":0.80804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":888.0,"contact_point_centroid":[0.47945,0.04119,0.04994],"force_p95":466.11179,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":508.7685,"mean_force":430.15595,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49032,0.03883,0.05018]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.48499,0.03879,0.04998],"force_p95":74.31098,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.52079,"mean_force":69.04407,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49996,0.03937,0.05077]}],"total_contact_groups":2},"final_pose_error":0.05239,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49954,0.03935,0.05069],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":508.7685,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":358.0,"n_steps_budget":810.0,"object_pos_end":[0.48601,0.02933,0.22892],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15243,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48555,0.0293,0.18893],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.48384,0.03678,0.174],"object_pos_start":[0.48601,0.02933,0.22892],"object_to_goal_dist_end":0.10223,"object_to_goal_dist_start":0.15243,"object_z_max":0.22892,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48295,0.03672,0.13401],"tcp_start":[0.48555,0.0293,0.18893],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.48349,0.0385,0.1178],"object_pos_start":[0.48384,0.03678,0.174],"object_to_goal_dist_end":0.05642,"object_to_goal_dist_start":0.10223,"object_z_max":0.174,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.48216,0.03841,0.07782],"tcp_start":[0.48295,0.03672,0.13401],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49746,0.03925,0.09063],"object_pos_start":[0.48349,0.0385,0.1178],"object_to_goal_dist_end":0.04074,"object_to_goal_dist_start":0.05642,"object_z_max":0.1178,"peak_contact_force":420.11793,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":888.0,"raw_peak_contact_force":508.7685,"subtask_id":"insert_peg","tcp_end":[0.49954,0.03935,0.05069],"tcp_start":[0.48216,0.03841,0.07782],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49796,0.03928,0.09073],"object_pos_start":[0.49746,0.03925,0.09063],"object_to_goal_dist_end":0.04076,"object_to_goal_dist_start":0.04074,"object_z_max":0.09073,"peak_contact_force":65.28298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":75.52079,"tcp_end":[0.50012,0.03938,0.05078],"tcp_start":[0.49954,0.03935,0.05069],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```