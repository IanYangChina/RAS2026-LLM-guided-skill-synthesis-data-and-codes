## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0831 | 0.57 | ❌ rejected |
| 5 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.4379 | 0.82 | ❌ rejected |
| 4 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.3951 | 0.86 | ❌ rejected |
| 3 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3393 | 0.74 | ❌ rejected |
| 2 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5025 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.083) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_hole
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
- id: approach_hole
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
- id: align_hole
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
- id: descend_insert
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
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_peg
- id: release_peg
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **release_peg** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.083
- **task_score** (E): 0.566
- **fitness_score**: 0.393  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.1064 |
| align_hole | 0.00 | 0.00 | 0.0007 |
| descend_insert | 0.00 | 1.00 | 0.0028 |
| release_peg | 1.00 | 1.00 | 0.0168 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.011, 0.198) | (0.504, -0.000, 0.340)→(0.512, -0.011, 0.238) | 0.260→0.161 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / guard_failure | (0.508, -0.011, 0.197)→(0.509, -0.011, 0.196) | (0.512, -0.011, 0.238)→(0.512, -0.011, 0.237) | 0.161→0.160 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / guard_failure | (0.580, 0.013, 0.011)→(0.579, 0.012, 0.008) | (0.513, -0.011, 0.236)→(0.604, 0.020, 0.046) | 0.159→0.112 | 1.00 / 1.667 | 8121.338 | 8213.130 |
| release_peg | release | 1.00 / step_budget | (0.579, 0.012, 0.008)→(0.585, 0.012, 0.010) | (0.603, 0.019, 0.040)→(0.608, 0.019, 0.041) | 0.113→0.118 | 1.00 / 1.000 | 79.721 | 21464.465 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.768
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.768
- phase_score: 0.354
- phase_breakdown.reach_above_hole_score: 0.537
- phase_breakdown.insert_peg_score: 0.275

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.519
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.768
- **Median Q (composite search score)**: 0.034
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.466


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.18182,"average_mean_iterations":43.21212,"average_solve_count":66.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.06987,"approach_hole.approach_speed":0.07073,"descend_insert.force_guard_threshold":34.29354,"descend_insert.insert_depth":0.10085,"descend_insert.insert_speed":0.04242},"optimized_scores":{"best_composite_score":0.03393,"best_fitness_score":0.34393,"best_task_score":0.46838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":200.0,"contact_point_centroid":[0.61318,0.01037,-0.00108],"force_p95":14011.96323,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33730.76569,"mean_force":2157.30766,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.60291,0.00497,0.00735]},{"body_a":"attachment","body_b":"peg_socket","contact_count":22.0,"contact_point_centroid":[0.58737,0.00556,0.00374],"force_p95":32221.55636,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32294.16871,"mean_force":17901.60731,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.59668,0.00328,-0.00465]},{"body_a":"attachment","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.60897,0.01074,-0.00401],"force_p95":12176.615,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12450.55572,"mean_force":9387.67901,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.59832,0.00567,0.00125]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.58774,0.00832,0.00916],"force_p95":11143.78199,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11425.613,"mean_force":8307.44573,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.59832,0.00567,0.00125]}],"total_contact_groups":4},"final_pose_error":0.07153,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.59559,0.00471,-0.00383],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":33730.76569,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.52616,-0.01378,0.23748],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16023,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52158,-0.01377,0.19775],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.52644,-0.01373,0.23699],"object_pos_start":[0.52616,-0.01378,0.23748],"object_to_goal_dist_end":0.15979,"object_to_goal_dist_start":0.16023,"object_z_max":0.23748,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52283,-0.01391,0.19623],"tcp_start":[0.52225,-0.01387,0.19675],"tcp_to_object_dist_end":0.04092,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.6204,0.01638,0.03241],"object_pos_start":[0.52751,-0.01387,0.23596],"object_to_goal_dist_end":0.1305,"object_to_goal_dist_start":0.15897,"object_z_max":0.23596,"peak_contact_force":12450.55572,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":12450.55572,"subtask_id":"insert_peg","tcp_end":[0.59559,0.00471,-0.00383],"tcp_start":[0.59667,0.00516,-0.00182],"tcp_to_object_dist_end":0.04544,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62604,0.01703,0.04043],"object_pos_start":[0.61854,0.0158,0.027],"object_to_goal_dist_end":0.1332,"object_to_goal_dist_start":0.13081,"object_z_max":0.04044,"peak_contact_force":92.28045,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":222.0,"raw_peak_contact_force":33730.76569,"tcp_end":[0.60372,0.00518,0.00942],"tcp_start":[0.59559,0.00471,-0.00383],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.2931,"average_mean_iterations":66.5,"average_solve_count":58.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.07541,"approach_hole.approach_speed":0.11587,"descend_insert.force_guard_threshold":33.69023,"descend_insert.insert_depth":0.096,"descend_insert.insert_speed":0.01824},"optimized_scores":{"best_composite_score":0.006,"best_fitness_score":0.316,"best_task_score":0.46185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":200.0,"contact_point_centroid":[0.62008,0.03539,-0.0011],"force_p95":12312.65772,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29572.69342,"mean_force":1706.54341,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.6093,0.0302,0.00685]},{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.59462,0.03205,0.00438],"force_p95":27980.20999,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28175.15972,"mean_force":12207.09476,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.60503,0.02976,-0.00357]},{"body_a":"attachment","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.6171,0.03919,-0.00335],"force_p95":11059.56464,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11288.49444,"mean_force":8458.43146,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.60585,0.03437,0.00197]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.59481,0.03618,0.00971],"force_p95":9979.10739,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10233.0517,"mean_force":7315.52358,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.60585,0.03437,0.00197]}],"total_contact_groups":4},"final_pose_error":0.08823,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.60348,0.03256,-0.0031],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":29572.69342,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":217.0,"n_steps_budget":720.0,"object_pos_end":[0.53196,-0.01905,0.23656],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16092,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52737,-0.01903,0.19683],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.53226,-0.01902,0.23608],"object_pos_start":[0.53196,-0.01905,0.23656],"object_to_goal_dist_end":0.16051,"object_to_goal_dist_start":0.16092,"object_z_max":0.23656,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52868,-0.01923,0.19536],"tcp_start":[0.52808,-0.01917,0.19587],"tcp_to_object_dist_end":0.04088,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.62689,0.04353,0.03434],"object_pos_start":[0.53337,-0.0192,0.23509],"object_to_goal_dist_end":0.1417,"object_to_goal_dist_start":0.15979,"object_z_max":0.23509,"peak_contact_force":11288.49444,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":11288.49444,"subtask_id":"insert_peg","tcp_end":[0.60348,0.03256,-0.0031],"tcp_start":[0.60442,0.03336,-0.00107],"tcp_to_object_dist_end":0.0455,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63158,0.0408,0.04092],"object_pos_start":[0.62535,0.04216,0.02899],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14175,"object_z_max":0.04092,"peak_contact_force":100.03765,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":225.0,"raw_peak_contact_force":29572.69342,"tcp_end":[0.60995,0.03028,0.00896],"tcp_start":[0.60348,0.03256,-0.0031],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":21.0,"average_failure_rate":0.32812,"average_mean_iterations":72.5625,"average_solve_count":64.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.03239,"approach_hole.approach_speed":0.10084,"descend_insert.force_guard_threshold":49.0974,"descend_insert.insert_depth":0.14979,"descend_insert.insert_speed":0.02502},"optimized_scores":{"best_composite_score":0.20949,"best_fitness_score":0.51949,"best_task_score":0.76801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":36.0,"contact_point_centroid":[0.55596,-7e-05,-0.00302],"force_p95":866.95308,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.93502,"mean_force":179.36081,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.54447,-0.00029,0.00358]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.52972,-8e-05,0.05131],"force_p95":855.32402,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":900.34107,"mean_force":450.17053,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.5402,-0.00017,0.04123]},{"body_a":"attachment","body_b":"peg_socket","contact_count":148.0,"contact_point_centroid":[0.53022,-0.00016,0.02097],"force_p95":60.5054,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.09879,"mean_force":59.84649,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.54173,-0.00032,0.01143]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.52888,0.00013,0.04625],"force_p95":623.68533,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":624.96254,"mean_force":612.19047,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.53935,-5e-05,0.03709]}],"total_contact_groups":4},"final_pose_error":0.12229,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.53921,-3e-05,0.03124],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":1089.93502,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":198.0,"n_steps_budget":780.0,"object_pos_end":[0.47871,-6e-05,0.23923],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16064,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47417,-6e-05,0.19948],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.47873,-5e-05,0.23871],"object_pos_start":[0.47871,-6e-05,0.23923],"object_to_goal_dist_end":0.16013,"object_to_goal_dist_start":0.16064,"object_z_max":0.23923,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.4746,-4e-05,0.19787],"tcp_start":[0.47432,-5e-05,0.19843],"tcp_to_object_dist_end":0.04104,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.56383,0.00033,0.07088],"object_pos_start":[0.47923,-2e-05,0.2376],"object_to_goal_dist_end":0.06448,"object_to_goal_dist_start":0.15897,"object_z_max":0.2376,"peak_contact_force":624.96254,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":900.34107,"subtask_id":"insert_peg","tcp_end":[0.53921,-3e-05,0.03124],"tcp_start":[0.53914,9e-05,0.03508],"tcp_to_object_dist_end":0.04667,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56716,0.00016,0.04135],"object_pos_start":[0.56407,0.00049,0.06257],"object_to_goal_dist_end":0.07749,"object_to_goal_dist_start":0.0664,"object_z_max":0.06257,"peak_contact_force":46.84464,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":184.0,"raw_peak_contact_force":1089.93502,"tcp_end":[0.54169,-0.00037,0.0105],"tcp_start":[0.53921,-3e-05,0.03124],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```