## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0186 | 0.16 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.1681 | 0.16 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.1022 | 0.16 | ✅ accepted |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.019) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  metric: contact
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.015
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_object
- id: grasp_close
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_up
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    orientation:
      mode: keep_current
  parameters:
    place_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_object
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_up** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.03
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.019
- **task_score** (E): 0.163
- **fitness_score**: 0.539  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1455 |
| descend_to_grasp | 1.00 | 0.1015 |
| grasp_close | 1.00 | 0.0111 |
| lift_up | 1.00 | 0.1165 |
| transport_to_goal | 0.00 | 0.1549 |
| descend_to_place | 1.00 | 0.0001 |
| release_object | 1.00 | 0.0239 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.161) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.490, -0.014, 0.161)→(0.488, -0.015, 0.059) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| grasp_close | grasp | 1.00 / step_budget | (0.488, -0.015, 0.059)→(0.481, -0.015, 0.051) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| lift_up | lift | 1.00 / step_budget | (0.481, -0.015, 0.051)→(0.477, -0.015, 0.168) | (0.493, -0.015, 0.026)→(0.487, -0.017, 0.122) | 0.281→0.250 |
| transport_to_goal | approach | 0.00 / step_budget | (0.477, -0.015, 0.168)→(0.520, 0.041, 0.303) | (0.487, -0.017, 0.122)→(0.496, 0.001, 0.016) | 0.250→0.274 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.520, 0.041, 0.303)→(0.520, 0.041, 0.303) | (0.496, 0.001, 0.016)→(0.496, 0.001, 0.016) | 0.274→0.274 |
| release_object | release | 1.00 / step_budget | (0.520, 0.041, 0.303)→(0.517, 0.040, 0.326) | (0.496, 0.001, 0.016)→(0.496, 0.001, 0.016) | 0.274→0.274 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.199
- phase_score: 0.512
- phase_breakdown.approach_object_score: 0.400
- phase_breakdown.place_at_goal_score: 0.031
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_clearance_score: 0.614
- grasp_place_fitness: 0.559

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.559
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.199
- **Median Q (composite search score)**: -0.028
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82759,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.09971,"approach_above.approach_speed":0.17976,"descend_to_grasp.descend_speed":0.03735,"descend_to_grasp.descend_tolerance":0.00535,"descend_to_place.place_force_threshold":6.83855,"descend_to_place.place_speed":0.03751,"lift_up.lift_height":0.14329,"lift_up.lift_speed":0.10597,"release_object.release_timeout":0.7906,"transport_to_goal.transport_arc_height":0.14817,"transport_to_goal.transport_speed":0.15258},"optimized_scores":{"best_composite_score":-0.02907,"best_fitness_score":0.52807,"best_task_score":0.14228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3803.0,"contact_point_centroid":[0.48046,-0.02114,-0.00224],"force_p95":0.12562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5558,"mean_force":0.1353,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46203,-0.01563,0.2758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7094.0,"contact_point_centroid":[0.46384,-0.00119,0.09981],"force_p95":0.13923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35706,"mean_force":0.09957,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46074,-0.01957,0.1024]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.47343,-0.01918,-0.00125],"force_p95":0.24749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35674,"mean_force":0.0578,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46293,-0.01965,0.05315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8017.0,"contact_point_centroid":[0.46352,-0.03779,0.10224],"force_p95":0.12864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31011,"mean_force":0.08918,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46074,-0.01957,0.10502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02012,-0.00209],"force_p95":0.14671,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1726,"mean_force":0.12984,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46544,-0.01971,0.05236]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48657,-0.00896,0.21952]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47151,-0.01905,0.09732]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.48046,-0.02106,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49391,0.01695,0.34842]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48046,-0.02106,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.49195,0.01704,0.3519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4490.0,"contact_point_centroid":[0.46474,-0.0006,0.05147],"force_p95":0.09447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09874,"mean_force":0.04862,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46437,-0.01968,0.05126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4778.0,"contact_point_centroid":[0.46381,-0.03861,0.05118],"force_p95":0.08127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08605,"mean_force":0.04714,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46437,-0.01968,0.05127]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3760.0,"contact_point_centroid":[0.46274,-0.0151,0.28309],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01067,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46254,-0.01509,0.28083]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.49334,0.01716,0.34866],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.4932,0.01716,0.34629]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.49406,0.01695,0.35051],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01087,"mean_force":0.01087,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49391,0.01695,0.34842]}],"total_contact_groups":14},"final_pose_error":0.24721,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48046,-0.02106,0.01602],"final_tcp_position":[0.49397,0.01703,0.34838],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.47449,-0.01832,0.13917],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11318,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.47166,-0.01987,0.05878],"tcp_start":[0.47449,-0.01832,0.13917],"tcp_to_object_dist_end":0.03307,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01973,0.02543],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2885,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46434,-0.01968,0.05124],"tcp_start":[0.47166,-0.01987,0.05878],"tcp_to_object_dist_end":0.02836,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":788.0,"n_steps_budget":870.0,"object_pos_end":[0.47328,-0.02631,0.11321],"object_pos_start":[0.47609,-0.01973,0.02543],"object_to_goal_dist_end":0.25558,"object_to_goal_dist_start":0.2885,"object_z_max":0.13933,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46088,-0.01956,0.18287],"tcp_start":[0.46434,-0.01968,0.05124],"tcp_to_object_dist_end":0.07108,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48046,-0.02106,0.01602],"object_pos_start":[0.47328,-0.02631,0.11321],"object_to_goal_dist_end":0.2925,"object_to_goal_dist_start":0.25558,"object_z_max":0.11321,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.49391,0.01695,0.34842],"tcp_start":[0.46088,-0.01956,0.18287],"tcp_to_object_dist_end":0.33484,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48046,-0.02106,0.01602],"object_pos_start":[0.48046,-0.02106,0.01602],"object_to_goal_dist_end":0.2925,"object_to_goal_dist_start":0.2925,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.49397,0.01703,0.34838],"tcp_start":[0.49391,0.01695,0.34842],"tcp_to_object_dist_end":0.33481,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48046,-0.02106,0.01602],"object_pos_start":[0.48046,-0.02106,0.01602],"object_to_goal_dist_end":0.2925,"object_to_goal_dist_start":0.2925,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49134,0.01699,0.37276],"tcp_start":[0.49397,0.01703,0.34838],"tcp_to_object_dist_end":0.35893,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58209,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.12859,"approach_above.approach_speed":0.199,"descend_to_grasp.descend_speed":0.03678,"descend_to_grasp.descend_tolerance":0.0063,"descend_to_place.place_force_threshold":8.6347,"descend_to_place.place_speed":0.07476,"lift_up.lift_height":0.11356,"lift_up.lift_speed":0.08605,"release_object.release_timeout":0.37222,"transport_to_goal.transport_arc_height":0.07427,"transport_to_goal.transport_speed":0.10701},"optimized_scores":{"best_composite_score":-0.02848,"best_fitness_score":0.52867,"best_task_score":0.14781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.47134,-0.00966,-0.00235],"force_p95":0.12919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6028,"mean_force":0.14122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47311,0.01546,0.21958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8244.0,"contact_point_centroid":[0.44573,-0.0439,0.09856],"force_p95":0.11731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30598,"mean_force":0.08754,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4436,-0.02549,0.10182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7840.0,"contact_point_centroid":[0.44612,-0.00701,0.09924],"force_p95":0.11706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30559,"mean_force":0.09149,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4436,-0.02549,0.10232]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.45639,-0.0254,-0.00118],"force_p95":0.22445,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2941,"mean_force":0.04854,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44597,-0.02559,0.05527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.45209,-0.00105,0.16476],"force_p95":0.14259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22544,"mean_force":0.10434,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44574,-0.01942,0.1682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2123.0,"contact_point_centroid":[0.45195,-0.03722,0.16526],"force_p95":0.11343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18268,"mean_force":0.09021,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44596,-0.0191,0.16883]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02626,-0.00205],"force_p95":0.13946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18079,"mean_force":0.12668,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44838,-0.02569,0.05464]},{"body_a":"world","body_b":"grasp_target","contact_count":1492.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.47939,-0.01141,0.2343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2663.0,"contact_point_centroid":[0.448,-0.00685,0.0509],"force_p95":0.101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12526,"mean_force":0.07607,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44735,-0.02565,0.05362]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45538,-0.02466,0.11303]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47133,-0.0095,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49453,0.04195,0.24443]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47133,-0.0095,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.49144,0.04177,0.24825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.44723,-0.0443,0.05068],"force_p95":0.09326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09362,"mean_force":0.06968,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44735,-0.02565,0.05362]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2699.0,"contact_point_centroid":[0.47477,0.01724,0.2241],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01067,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47456,0.01724,0.22181]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.49363,0.04198,0.2445],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01033,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.49348,0.04198,0.24248]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.4931,0.04195,0.24834],"force_p95":0.00951,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00951,"mean_force":0.00951,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49453,0.04195,0.24443]}],"total_contact_groups":16},"final_pose_error":0.24591,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.47133,-0.0095,0.01602],"final_tcp_position":[0.4946,0.042,0.24444],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.45933,-0.02354,0.16789],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1419,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.45443,-0.02592,0.06067],"tcp_start":[0.45933,-0.02354,0.16789],"tcp_to_object_dist_end":0.03489,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02582,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30336,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44732,-0.02565,0.05359],"tcp_start":[0.45443,-0.02592,0.06067],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":747.0,"n_steps_budget":840.0,"object_pos_end":[0.45018,-0.02546,0.12195],"object_pos_start":[0.4585,-0.02582,0.02582],"object_to_goal_dist_end":0.29504,"object_to_goal_dist_start":0.30336,"object_z_max":0.12185,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44368,-0.02548,0.15706],"tcp_start":[0.44732,-0.02565,0.05359],"tcp_to_object_dist_end":0.03571,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47133,-0.0095,0.01602],"object_pos_start":[0.45018,-0.02546,0.12195],"object_to_goal_dist_end":0.28678,"object_to_goal_dist_start":0.29504,"object_z_max":0.14286,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.49453,0.04195,0.24443],"tcp_start":[0.44368,-0.02548,0.15706],"tcp_to_object_dist_end":0.23528,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47133,-0.0095,0.01602],"object_pos_start":[0.47133,-0.0095,0.01602],"object_to_goal_dist_end":0.28678,"object_to_goal_dist_start":0.28678,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.4946,0.042,0.24444],"tcp_start":[0.49453,0.04195,0.24443],"tcp_to_object_dist_end":0.23531,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47133,-0.0095,0.01602],"object_pos_start":[0.47133,-0.0095,0.01602],"object_to_goal_dist_end":0.28678,"object_to_goal_dist_start":0.28678,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49028,0.04165,0.26922],"tcp_start":[0.4946,0.042,0.24444],"tcp_to_object_dist_end":0.25901,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69091,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.13918,"approach_above.approach_speed":0.2021,"descend_to_grasp.descend_speed":0.04896,"descend_to_grasp.descend_tolerance":0.00593,"descend_to_place.place_force_threshold":3.90725,"descend_to_place.place_speed":0.06623,"lift_up.lift_height":0.12922,"lift_up.lift_speed":0.15432,"release_object.release_timeout":0.43411,"transport_to_goal.transport_arc_height":0.17916,"transport_to_goal.transport_speed":0.17828},"optimized_scores":{"best_composite_score":0.00181,"best_fitness_score":0.55895,"best_task_score":0.19861},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3114.0,"contact_point_centroid":[0.53496,0.03359,-0.0023],"force_p95":0.13071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4337,"mean_force":0.13955,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53999,0.02114,0.2664]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.54184,0.00095,-0.00116],"force_p95":0.24431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42661,"mean_force":0.06859,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.5292,0.00087,0.05023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1318.0,"contact_point_centroid":[0.52988,0.01678,0.17041],"force_p95":0.20345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36507,"mean_force":0.10011,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52336,-0.00106,0.17188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8356.0,"contact_point_centroid":[0.52979,0.01956,0.09594],"force_p95":0.10427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32219,"mean_force":0.06727,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52687,0.00084,0.09552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7846.0,"contact_point_centroid":[0.52916,-0.01805,0.09353],"force_p95":0.13202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30316,"mean_force":0.07312,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52688,0.00084,0.09376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.52979,-0.01917,0.16749],"force_p95":0.17811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26259,"mean_force":0.11471,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52368,-0.00085,0.17055]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00111,-0.00203],"force_p95":0.132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15227,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53202,0.00092,0.05007]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51704,0.00048,0.23683]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53619,0.00099,0.11428]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.53498,0.03381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57254,0.0626,0.31489]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53498,0.03381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57021,0.06257,0.31664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4545.0,"contact_point_centroid":[0.53103,-0.01826,0.04944],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10603,"mean_force":0.04759,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53082,0.0009,0.04863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4689.0,"contact_point_centroid":[0.53154,0.02006,0.04979],"force_p95":0.07025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08432,"mean_force":0.04625,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53082,0.0009,0.04864]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3164.0,"contact_point_centroid":[0.54091,0.02206,0.27129],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54073,0.02206,0.26899]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57202,0.0629,0.31447],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57172,0.06289,0.3122]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.57115,0.06261,0.31881],"force_p95":0.00949,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00949,"mean_force":0.00949,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57254,0.0626,0.31489]}],"total_contact_groups":16},"final_pose_error":0.1663,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.53498,0.03381,0.01602],"final_tcp_position":[0.5726,0.06273,0.31482],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53652,0.00098,0.17521],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14939,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.53894,0.00104,0.05844],"tcp_start":[0.53652,0.00098,0.17521],"tcp_to_object_dist_end":0.03286,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00099,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25035,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53079,0.0009,0.0486],"tcp_start":[0.53894,0.00104,0.05844],"tcp_to_object_dist_end":0.0264,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53724,0.00187,0.13135],"object_pos_start":[0.54422,0.00099,0.02586],"object_to_goal_dist_end":0.20039,"object_to_goal_dist_start":0.25035,"object_z_max":0.13119,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52705,0.00085,0.16276],"tcp_start":[0.53079,0.0009,0.0486],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53498,0.03381,0.01602],"object_pos_start":[0.53724,0.00187,0.13135],"object_to_goal_dist_end":0.24246,"object_to_goal_dist_start":0.20039,"object_z_max":0.14806,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.57254,0.0626,0.31489],"tcp_start":[0.52705,0.00085,0.16276],"tcp_to_object_dist_end":0.30259,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53498,0.03381,0.01602],"object_pos_start":[0.53498,0.03381,0.01602],"object_to_goal_dist_end":0.24246,"object_to_goal_dist_start":0.24246,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.5726,0.06273,0.31482],"tcp_start":[0.57254,0.0626,0.31489],"tcp_to_object_dist_end":0.30255,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53498,0.03381,0.01602],"object_pos_start":[0.53498,0.03381,0.01602],"object_to_goal_dist_end":0.24246,"object_to_goal_dist_start":0.24246,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.56944,0.06241,0.33675],"tcp_start":[0.5726,0.06273,0.31482],"tcp_to_object_dist_end":0.32384,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```