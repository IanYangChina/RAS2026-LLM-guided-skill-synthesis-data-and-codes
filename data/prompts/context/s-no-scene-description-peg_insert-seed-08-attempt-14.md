## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14 | -0.1033 | 0.83 | ❌ rejected |
| 13 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2129 | 0.85 | ❌ rejected |
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0451 | 0.84 | ❌ rejected |
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1831 | 0.85 | ❌ rejected |
| 10 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 9 | -0.0302 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.103) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_socket_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.2
- id: insertion_depth
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_to_socket
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
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
    approach_arc:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_above_socket
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_socket_entry
- id: insert_peg
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.055
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 40.0
      - 80.0
      default: 50.0
      binds_to:
      - path: guards.force_limit_guard.threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tol:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.006
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.006
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.006
    - 0.006
    - 0.0
  subtask_id: insertion_depth

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_arc: status=consumed; consumers=generator.arc_height (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **insert_peg** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.055, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_limit_guard.threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.006, 0.006, 0.0]

## Design Metrics

- **Composite score**: -0.103
- **task_score** (E): 0.835
- **fitness_score**: 0.490  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.760

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.00 | 0.67 | 0.1266 |
| align_over_socket | 0.67 | 0.67 | 0.0887 |
| descend_to_rim | 0.67 | 0.67 | 0.0166 |
| insert_peg | 0.00 | 0.00 | 0.0769 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.461, 0.005, 0.182) | (0.504, -0.000, 0.340)→(0.497, 0.005, 0.165) | 0.260→0.088 | 0.67 / 1.000 | 174.020 | 1543.385 |
| align_over_socket | align | 0.67 / step_budget | (0.461, 0.005, 0.182)→(0.509, 0.005, 0.223) | (0.497, 0.005, 0.165)→(0.546, 0.004, 0.212) | 0.088→0.146 | 0.67 / 0.667 | 121.648 | 319.951 |
| descend_to_rim | descend | 0.67 / force_exceeded | (0.509, 0.005, 0.223)→(0.506, 0.006, 0.239) | (0.546, 0.004, 0.212)→(0.544, 0.005, 0.230) | 0.146→0.163 | 0.67 / 0.667 | 117.106 | 159.363 |
| insert_peg | insert | 0.00 / guard_failure | (0.506, 0.005, 0.239)→(0.505, 0.004, 0.162) | (0.544, 0.005, 0.230)→(0.543, 0.004, 0.153) | 0.163→0.090 | 0.00 / 0.000 | 0.000 | 194.322 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.806
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.806
- phase_score: 0.247
- phase_breakdown.reach_above_socket_score: 0.483
- phase_breakdown.insertion_depth_score: 0.000
- phase_breakdown.reach_aligned_score: 0.511

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.569
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.861
- **Median Q (composite search score)**: -0.080
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.315


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6af64227b04102c511381eb024ec48290b429fbc7fcb6f0c4b42c66d0a974e9f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5cd76595591baa0f9f71873dced18f865534f529ba8f9daf4a3973579a78fb36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.30303,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_socket.align_speed":0.03664,"align_over_socket.align_tol":0.01299,"approach_high.approach_arc":0.08171,"approach_high.approach_height":0.21173,"approach_high.approach_speed":0.06689,"approach_high.approach_tol":0.01332,"descend_to_rim.descend_speed":0.01876,"descend_to_rim.force_threshold":8.37177,"insert_peg.force_limit":26.02156,"insert_peg.insert_depth":0.06501,"insert_peg.insert_speed":0.0145,"insert_peg.insert_tol":0.02483,"insert_peg.retry_offset_x":0.00755,"insert_peg.retry_offset_y":0.00957},"optimized_scores":{"best_composite_score":-0.03925,"best_fitness_score":0.47075,"best_task_score":0.80596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.54434,0.02631,0.07978],"force_p95":318.19794,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.32304,"mean_force":183.88071,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44277,0.02156,0.1722]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.44138,0.0123,0.07922],"force_p95":536.16125,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":893.60208,"mean_force":99.28912,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.43733,0.01226,0.09288]},{"body_a":"peg_socket","body_b":"link6","contact_count":442.0,"contact_point_centroid":[0.54611,0.02744,0.07965],"force_p95":339.13727,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":469.53292,"mean_force":238.91618,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44487,0.02256,0.17966]},{"body_a":"peg_socket","body_b":"link7","contact_count":762.0,"contact_point_centroid":[0.5461,0.03646,0.07995],"force_p95":313.89421,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":438.40017,"mean_force":186.92077,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.4758,0.03203,0.18336]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54615,0.04427,0.08],"force_p95":310.96394,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.64454,"mean_force":233.41733,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49,0.04013,0.15799]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54614,0.03209,0.07999],"force_p95":306.23805,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.52585,"mean_force":231.6479,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.45679,0.02449,0.19089]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54614,0.04415,0.08],"force_p95":217.59748,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.93607,"mean_force":160.55014,"phase_index":2.0,"phase_name":"descend_to_rim","phase_type":"descend","tcp_position_centroid":[0.48997,0.03995,0.15822]}],"total_contact_groups":7},"final_pose_error":0.19799,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49002,0.0401,0.15794],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1082.32304,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49014,0.02622,0.16894],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09324,"object_to_goal_dist_start":0.26034,"object_z_max":0.34404,"peak_contact_force":258.44959,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":980.0,"raw_peak_contact_force":1082.32304,"subtask_id":"reach_above_socket","tcp_end":[0.45678,0.0245,0.19092],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":815.0,"n_steps_budget":960.0,"object_pos_end":[0.52469,0.04081,0.13855],"object_pos_start":[0.49014,0.02622,0.16894],"object_to_goal_dist_end":0.07552,"object_to_goal_dist_start":0.09324,"object_z_max":0.16982,"peak_contact_force":244.0404,"phase_name":"align_over_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":764.0,"raw_peak_contact_force":438.40017,"subtask_id":"reach_aligned","tcp_end":[0.48993,0.03978,0.1583],"tcp_start":[0.45678,0.0245,0.19092],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.52475,0.04113,0.13826],"object_pos_start":[0.52469,0.04081,0.13855],"object_to_goal_dist_end":0.07549,"object_to_goal_dist_start":0.07552,"object_z_max":0.1386,"peak_contact_force":97.16422,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":223.93607,"tcp_end":[0.48999,0.04013,0.15803],"tcp_start":[0.48993,0.03978,0.1583],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52477,0.04111,0.13823],"object_pos_start":[0.52475,0.04113,0.13826],"object_to_goal_dist_end":0.07546,"object_to_goal_dist_start":0.07549,"object_z_max":0.13826,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":320.64454,"subtask_id":"insertion_depth","tcp_end":[0.49002,0.0401,0.15794],"tcp_start":[0.49001,0.04011,0.15797],"tcp_to_object_dist_end":0.03996,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":170.0,"average_failure_rate":0.52795,"average_mean_iterations":109.59627,"average_solve_count":322.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_socket.align_speed":0.02681,"align_over_socket.align_tol":0.01327,"approach_high.approach_arc":0.06261,"approach_high.approach_height":0.19939,"approach_high.approach_speed":0.05752,"approach_high.approach_tol":0.01301,"descend_to_rim.descend_speed":0.01477,"descend_to_rim.force_threshold":5.09977,"insert_peg.force_limit":22.87095,"insert_peg.insert_depth":0.05597,"insert_peg.insert_speed":0.00958,"insert_peg.insert_tol":0.01966,"insert_peg.retry_offset_x":0.00624,"insert_peg.retry_offset_y":0.00745},"optimized_scores":{"best_composite_score":-0.19077,"best_fitness_score":0.56923,"best_task_score":0.83653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.54016,0.01307,0.0771],"force_p95":950.22986,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1121.06987,"mean_force":239.24549,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44494,0.0093,0.10409]},{"body_a":"peg_socket","body_b":"link7","contact_count":291.0,"contact_point_centroid":[0.58957,-0.00754,0.07994],"force_p95":267.95458,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.80053,"mean_force":195.37207,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.4999,-0.00128,0.1779]},{"body_a":"peg_socket","body_b":"link6","contact_count":731.0,"contact_point_centroid":[0.58934,0.01101,0.07985],"force_p95":279.86017,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.05341,"mean_force":240.71711,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45255,0.01319,0.16583]},{"body_a":"peg_socket","body_b":"link6","contact_count":400.0,"contact_point_centroid":[0.58959,0.00318,0.07995],"force_p95":145.85385,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.95171,"mean_force":131.25718,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.48248,0.00466,0.19124]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.55993,0.00922,0.07821],"force_p95":177.33165,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.86653,"mean_force":37.01316,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44466,0.0093,0.10392]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54111,-0.04715,0.07939],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44353,0.00924,0.09454]}],"total_contact_groups":6},"final_pose_error":0.21205,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52735,-0.00485,0.18071],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1121.06987,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50008,0.00926,0.1804],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10083,"object_to_goal_dist_start":0.26034,"object_z_max":0.34442,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":811.0,"raw_peak_contact_force":1121.06987,"subtask_id":"reach_above_socket","tcp_end":[0.46519,0.01084,0.1999],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5782,-0.00489,0.35805],"object_pos_start":[0.50008,0.00926,0.1804],"object_to_goal_dist_end":0.28888,"object_to_goal_dist_start":0.10083,"object_z_max":0.35652,"peak_contact_force":0.0,"phase_name":"align_over_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":691.0,"raw_peak_contact_force":304.80053,"subtask_id":"reach_aligned","tcp_end":[0.53852,-0.0031,0.3628],"tcp_start":[0.46519,0.01084,0.1999],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.57116,-0.00266,0.41202],"object_pos_start":[0.5782,-0.00489,0.35805],"object_to_goal_dist_end":0.33957,"object_to_goal_dist_start":0.28888,"object_z_max":0.41157,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5312,-0.00096,0.41136],"tcp_start":[0.53852,-0.0031,0.3628],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.56732,-0.00646,0.18044],"object_pos_start":[0.57116,-0.00266,0.41202],"object_to_goal_dist_end":0.12109,"object_to_goal_dist_start":0.33957,"object_z_max":0.41269,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_depth","tcp_end":[0.52735,-0.00485,0.18071],"tcp_start":[0.5312,-0.00096,0.41136],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":27.0,"average_failure_rate":0.2967,"average_mean_iterations":62.79121,"average_solve_count":91.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_socket.align_speed":0.02357,"align_over_socket.align_tol":0.01084,"approach_high.approach_arc":0.05475,"approach_high.approach_height":0.24285,"approach_high.approach_speed":0.06073,"approach_high.approach_tol":0.01489,"descend_to_rim.descend_speed":0.01333,"descend_to_rim.force_threshold":7.01931,"insert_peg.force_limit":34.61514,"insert_peg.insert_depth":0.05597,"insert_peg.insert_speed":0.00899,"insert_peg.insert_tol":0.02346,"insert_peg.retry_offset_x":0.00678,"insert_peg.retry_offset_y":0.00791},"optimized_scores":{"best_composite_score":-0.08,"best_fitness_score":0.43,"best_task_score":0.86118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.59639,-0.01976,0.07973],"force_p95":1587.5857,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2426.76197,"mean_force":395.33611,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46171,-0.01582,0.14008]},{"body_a":"peg_socket","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.5883,-0.01138,0.07928],"force_p95":1920.615,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2113.35799,"mean_force":526.27664,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46322,-0.01313,0.12815]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.5512,0.00732,0.07867],"force_p95":211.29553,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.90764,"mean_force":42.455,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45585,-0.01236,0.10011]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.59647,-0.02279,0.07998],"force_p95":261.71347,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.32107,"mean_force":256.24507,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49758,-0.02271,0.14791]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59647,-0.02259,0.07997],"force_p95":254.15366,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.15366,"mean_force":254.15366,"phase_index":2.0,"phase_name":"descend_to_rim","phase_type":"descend","tcp_position_centroid":[0.49738,-0.02248,0.14796]},{"body_a":"peg_socket","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.59647,-0.02295,0.07994],"force_p95":188.93531,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.6517,"mean_force":118.25654,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.46699,-0.02044,0.1563]},{"body_a":"peg_socket","body_b":"link7","contact_count":97.0,"contact_point_centroid":[0.59647,-0.01858,0.07997],"force_p95":130.36648,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.3533,"mean_force":94.11835,"phase_index":1.0,"phase_name":"align_over_socket","phase_type":"align","tcp_position_centroid":[0.48352,-0.02126,0.15186]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.55157,-0.05358,0.07892],"force_p95":9.92668,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.63338,"mean_force":2.91961,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45548,-0.01231,0.09816]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.47651,-0.01169,0.0799],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46177,-0.01164,0.09104]}],"total_contact_groups":9},"final_pose_error":0.18302,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.49767,-0.02301,0.14789],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":2426.76197,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.49928,-0.02007,0.14607],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06906,"object_to_goal_dist_start":0.26034,"object_z_max":0.34541,"peak_contact_force":263.61018,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":2426.76197,"subtask_id":"reach_above_socket","tcp_end":[0.46022,-0.01998,0.15471],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.53635,-0.02263,0.13892],"object_pos_start":[0.49928,-0.02007,0.14607],"object_to_goal_dist_end":0.07283,"object_to_goal_dist_start":0.06906,"object_z_max":0.14809,"peak_contact_force":120.90476,"phase_name":"align_over_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":212.0,"raw_peak_contact_force":216.6517,"subtask_id":"reach_aligned","tcp_end":[0.49738,-0.02248,0.14796],"tcp_start":[0.46022,-0.01998,0.15471],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5365,-0.02277,0.13888],"object_pos_start":[0.53635,-0.02263,0.13892],"object_to_goal_dist_end":0.07292,"object_to_goal_dist_start":0.07283,"object_z_max":0.13892,"peak_contact_force":254.15366,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":254.15366,"tcp_end":[0.49753,-0.02263,0.14792],"tcp_start":[0.49738,-0.02248,0.14796],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,-0.02293,0.13887],"object_pos_start":[0.5365,-0.02277,0.13888],"object_to_goal_dist_end":0.07301,"object_to_goal_dist_start":0.07292,"object_z_max":0.13888,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":262.32107,"subtask_id":"insertion_depth","tcp_end":[0.49767,-0.02301,0.14789],"tcp_start":[0.49767,-0.02293,0.14788],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```